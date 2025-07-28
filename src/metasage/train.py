from typing import Any
import pandas as pd
import xgboost as xgb
import polars as pl
from sklearn.model_selection import (
    KFold,
    train_test_split,
)
import pickle
import shap
import os
import seaborn as sns
import numpy as np
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    explained_variance_score,
)
import matplotlib.pyplot as plt
from metasage.analysis import new_plot_max_weighted, plot_max_weighted
from metasage.build import extract_base_gene, get_host_cols, ppi_genes
from metasage.utils.messages import print_info
from scipy.stats import zscore, spearmanr
from dataclasses import dataclass, field
import random

from metasage.utils.seeds import FixedSeedGeneratorByRun, SeedGenerator


class TooManyMissingSite(Exception):
    pass


@dataclass
class FeatureResult:
    """
    A class to represent the result of a feature in a machine learning model.

    Attributes:
    ----------
    name : str
        The name of the feature. Gene|Site_omictype (ABC1|S234_phospho)
    feature_value : float
        The value of the feature. (avg abs Shapley)
    corr : float
        The correlation of the feature with the top feature. (set to 0)
    is_best : bool, optional
        A flag indicating if this feature is the best one (default is False). (ignore)
    _experimental : dict[str, Any], optional
        An optional dictionary to store experimental values related to the feature (default is an empty dictionary).
    """

    name: str
    value: float
    corr: float
    is_best: bool = False
    _experimental: dict[str, Any] = field(
        default_factory=lambda: {}
    )  # Optional dictionary of values


@dataclass
class ModelResult:
    site: str
    features: list[FeatureResult]
    p_val: float
    corr: float
    top_feat_corr: float  # correlation of top feature to prediction


def feature_result_to_dict(
    res: FeatureResult,
) -> dict[str, str | float | bool | dict[str, Any]]:
    return {
        "name": res.name,
        "value": res.value,
        "corr": res.corr,
        "is_best": res.is_best,
        "_experimental": res._experimental,
    }


def model_result_to_dict(
    res: ModelResult,
) -> dict[
    str, str | float | bool | list[dict[str, str | float | bool | dict[str, Any]]]
]:
    return {
        "site": res.site,
        "features": [feature_result_to_dict(feat) for feat in res.features],
        "p_val": res.p_val,
        "corr": res.corr,
        "top_feat_corr": res.top_feat_corr,
    }


def process_site(
    site: str,
    base_df: pl.DataFrame,
    only_label: bool = False,
    fixed_seed: bool = False,
    runs: int = 1,
) -> ModelResult:
    base_gene = extract_base_gene(site)
    host_df = get_host_cols(
        None,
        "phospho.tsv",
        ["rna.tsv", "protein.tsv"],
        site,
        "|",
        only_label=only_label,
    )
    valid_features = ppi_genes(base_gene)
    columns_to_keep = ["Sample"]

    for col in base_df.columns:
        check_col = col.removesuffix("_protein")
        check_col = check_col.removesuffix("_rna")
        check_col = check_col.removesuffix("_methyl")
        # Check if column's base gene is in valid_features
        if extract_base_gene(check_col) in valid_features:
            columns_to_keep.append(col)
    df = base_df.select(columns_to_keep)
    # Check if the 'label' column in host_df has less than 80% non-missing values
    not_nan_count = host_df["label"].drop_nans().shape[0]
    if not_nan_count / host_df.shape[0] < 0.8:
        raise TooManyMissingSite("Site less than 80% non-missing")
    df = df.join(host_df, on="Sample", how="full", coalesce=True)
    df = df.select(
        [
            col
            for col in df.columns
            if col == "label"
            or col != f"{site}_phospho"
            and not col.startswith(f"{base_gene}_rna")
            and not col.startswith(f"{base_gene}_protein")
            and df[[col, "label"]].drop_nans().shape[0] / not_nan_count >= 0.5
        ]
    )
    # df.write_csv("omic/citr_features.tsv", separator="\t", include_header=True)
    seed = random.randint(0, int(1e6))
    if fixed_seed:
        seed = FixedSeedGeneratorByRun(11232)
    return mini_train(site, df.to_pandas(), seed, runs=runs)


def mini_train(
    site: str,
    df: pd.DataFrame,
    seed: int | SeedGenerator,
    groups: list[int] | None = None,
    use_z=False,
    n_folds: int = 5,
    top_n: int = 10,
    runs=1,
) -> ModelResult:
    df = df.dropna(subset=["label"])
    df.set_index(df.columns[0], inplace=True)
    X = df.iloc[:, 1:-1]
    X.reset_index()
    y = df["label"]

    if use_z:
        X = X.apply(zscore)
        y = zscore(y)
    # skf = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=seed)

    # Run k-fold cross-validation
    y_real = np.zeros(len(y))
    y_pred = np.zeros(len(y))
    for run in range(runs):
        # print(run)
        run_seed = seed.get_seed(run=run)
        # print(run_seed)
        # if seed is SeedGenerator or seed is FixedSeedGeneratorByRun:
        #     run_seed = seed.get_seed(run=run)
        #     print("hello")
        # else:
        #     run_seed = seed
        skf = KFold(n_splits=n_folds, shuffle=True, random_state=run_seed)
        for fold, (train_idx, test_idx) in enumerate(skf.split(X, y, groups=groups)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            model = xgb.XGBRegressor(
                random_state=run_seed,
                objective="reg:squarederror",
            )
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            y_real[test_idx] += y_test
            y_pred[test_idx] += preds

    y_real /= runs
    y_pred /= runs
    stat_res = spearmanr(y, y_pred, nan_policy="omit")
    p_val = stat_res.pvalue
    r_sq = r2_score(y, y_pred)
    # if seed is SeedGenerator:
    #     run_seed = seed.get_seed(run=1)
    # else:
    run_seed = seed.get_seed(run=0)
    full_model = xgb.XGBRegressor(
        n_estimators=100,
        random_state=1,
        colsample_bytree=0.6,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.6,
        objective="reg:squarederror",
    )
    full_model.fit(X, y)
    explainer = shap.TreeExplainer(full_model)
    shap_values = explainer.shap_values(X)
    mean_abs_shap_values = np.abs(shap_values).mean(axis=0)
    top_features_idx = np.argsort(mean_abs_shap_values)[-top_n:][::-1]
    top_features = X.columns[top_features_idx]
    best_feature = top_features[0]
    best_y = X[best_feature]
    features: list[FeatureResult] = []
    (top_feat_corr, _) = spearmanr(y, best_y, nan_policy="omit")
    (model_corr, _) = spearmanr(y, y_pred, nan_policy="omit")
    top_feat_corr = float(model_corr) - float(top_feat_corr)
    # TODO: This should be done at a later stage, after models are selected. Currently saving all models.
    for feature in top_features:
        feature_value = mean_abs_shap_values[X.columns.get_loc(feature)]
        if feature == best_feature:  # skip calculation
            f_corr = 1.0
        else:
            res = spearmanr(X[feature], best_y, nan_policy="omit")
            f_corr: float = res.statistic
        features.append(
            FeatureResult(name=feature, value=float(feature_value), corr=float(f_corr))
        )

    model_result = ModelResult(
        site=site,
        features=features,
        p_val=float(p_val),
        corr=float(r_sq),
        top_feat_corr=float(top_feat_corr),
    )
    return model_result


def train_model(
    data_path: str = "data.parquet", output_dir="output", seed=42, use_z=False
):
    pl_df = pl.read_parquet(data_path)
    df = pl_df.to_pandas()
    df = df.dropna(subset=["label"])
    df.set_index(df.columns[0], inplace=True)
    X = df.iloc[:, 1:-1]
    X.reset_index()
    y = df["label"]
    feat_names = X.columns
    if use_z:
        X = X.apply(zscore)
        y = zscore(y)
    # y = y + 100
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )
    os.makedirs(output_dir, exist_ok=True)
    print_info("Saving training and testing data")
    with open(f"{output_dir}/training_data.pkl", "wb") as w:
        pickle.dump((X_train, y_train), w)
    with open(f"{output_dir}/testing_data.pkl", "wb") as w:
        pickle.dump((X_test, y_test), w)
    print_info("Training model")
    # param_grid = {
    #     "max_depth": [5, 7, 10],
    #     "learning_rate": [0.01, 0.05, 0.1],
    #     "subsample": [0.6, 0.8, 1.0],
    #     "colsample_bytree": [0.6, 0.8, 1.0],
    # }
    model = xgb.XGBRegressor(
        n_estimators=100,
        random_state=seed,
        colsample_bytree=0.6,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.6,
        objective="reg:squarederror",
    )

    # Initialize GridSearchCV with the model, parameter grid, and cross-validation
    # grid_search = GridSearchCV(
    #     estimator=model,
    #     param_grid=param_grid,
    #     cv=3,
    #     verbose=1,
    #     n_jobs=-1,
    #     scoring="neg_mean_squared_error",
    # )  # Fit the grid search to the training data
    # grid_search.fit(X_train, y_train)

    # # Get the best parameters and the best score
    # best_params = grid_search.best_params_
    # best_score = grid_search.best_score_

    # print("Best parameters found: ", best_params)
    # print("Best score found: ", best_score)

    # # Use the best model found in the grid search to fit the data
    # model = grid_search.best_estimator_
    model.fit(X_train, y_train)
    explainer = shap.Explainer(model)
    shap_exp = explainer(X_train)
    shap_values = explainer.shap_values(X_train)
    fig, ax = plt.subplots(figsize=(30, 30))
    xgb.plot_tree(model, num_trees=0, ax=ax)
    plt.savefig(f"{output_dir}/xgboost.pdf")
    plt.clf()
    plt.cla()
    plt.close()

    # st = SuperTree(model, X_train, y_train, feat_names, "Tree")
    # Visualize the tree
    # st.show_tree(which_tree=1)

    # Plot SHAP summary
    shap.plots.beeswarm(
        shap_exp,
        # features=X_train,
        # feature_names=feat_names,
        # plot_type="layered_violin",
        max_display=15,
        show=False,
        # group_remaining_features=False,
    )
    plt.tight_layout()
    plt.savefig(f"{output_dir}/global_shap.pdf")

    # Convert SHAP values to DataFrame
    shap_df = pd.DataFrame(shap_values, columns=X_train.columns)

    # Add corresponding sample index
    shap_df.insert(0, "Sample", X_train.index)

    # Save to TSV file
    shap_df.to_csv(f"{output_dir}/shap_values.tsv", sep="\t", index=False)

    print_info("SHAP values saved to shap_values.tsv")
    shap_importance = pd.DataFrame(
        {
            "Feature": X_test.columns,
            "Mean_SHAP": np.abs(shap_df.drop(columns=["Sample"])).mean(axis=0),
        }
    ).sort_values(by=["Mean_SHAP"], ascending=False)

    shap_importance.to_csv(
        f"{output_dir}/shap_featurefimportance.tsv", sep="\t", index=False
    )

    ## Retrain model to use top 10 features

    print_info("Feature importance saved to shap_feature_importance.tsv")

    print_info("Getting evaluation")
    # Predict on test set
    y_pred = model.predict(X_test)

    # Compute regression metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    evs = explained_variance_score(y_test, y_pred)

    # Print results
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"R² Score: {r2:.4f}")
    print(f"Explained Variance Score: {evs:.4f}")
    # Predict on the training data

    y_train_pred = model.predict(X_train)

    # Compute regression metrics for training data
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    train_mae = mean_absolute_error(y_train, y_train_pred)
    train_r2 = r2_score(y_train, y_train_pred)
    train_evs = explained_variance_score(y_train, y_train_pred)

    # Print results with context
    print(
        f"Training RMSE: {train_rmse:.4f} (Context: The true values are expected to be in the range of {min(y_train):.2f} to {max(y_train):.2f})"
    )
    print(
        f"Training MAE: {train_mae:.4f} (Context: The true values are expected to be in the range of {min(y_train):.2f} to {max(y_train):.2f})"
    )
    print(f"Training R² Score: {train_r2:.4f}")
    print(f"Training Explained Variance Score: {train_evs:.4f}")
    plt.clf()
    plt.cla()
    plt.close()
    sns.set_theme(context="talk", style="white")
    plt.figure(figsize=(5, 5))
    sns.regplot(x=y_test, y=y_pred)
    plt.xlabel("Real Value")
    plt.ylabel("Predicted Value")
    plt.title("Real vs. Predicted Site Abundance")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/regplot.pdf")

    plot_max_weighted(
        shap_values,
        feat_names,
        f"{output_dir}/max_weighted.pdf",
        num_features=15,
    )

    new_plot_max_weighted(
        shap_values,
        X_train.to_numpy(),
        feat_names,
        f"{output_dir}/complex_max_weighted.pdf",
        num_features=15,
    )
