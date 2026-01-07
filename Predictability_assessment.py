import numpy as np
import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import KFold
from scipy.stats import pearsonr

def assess():
    path = "~/feature/"
    with open(os.path.join("predictability_assessment_results.tsv"), "w") as fw_result:
        fw_result.write("meta\tpearson_corr\tp-value\n")
        for num, item in enumerate(os.listdir(path), start=1):
            print(f"{item}\t{num}")
            meta = item.split(".")[0]
            file = os.path.join(path, item)
            df = pd.read_csv(file, sep="\t", encoding="utf-8")
            df = df.set_index(df.columns[0])

            if "meta" not in df.columns:
                print(f"Skipping {item} - 'meta' column missing")
                continue

            X = df.drop(columns=["meta"]).fillna(0)
            X.columns = [str(col).replace('[', '_').replace(']', '_').replace('<', '_').replace('>', '_') for col in
                         X.columns]
            y = df["meta"].values
            num_features = X.shape[1]
            if num_features == 0:
                print(f"Skipping {item} - No valid features after dropping 'meta'")
                continue
            aggregated_preds = {idx: [] for idx in range(len(y))}
            for seed in range(1, 11):
                kf = KFold(n_splits=5, shuffle=True, random_state=seed)

                for train_index, test_index in kf.split(X):
                    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
                    y_train, y_test = y[train_index], y[test_index]

                    model = xgb.XGBRegressor(n_estimators=100, random_state=seed)
                    model.fit(X_train, y_train)

                    preds = model.predict(X_test)
                    # Store predictions per sample
                    for i, idx in enumerate(test_index):
                        aggregated_preds[idx].append(preds[i])

            # Compute final averaged predictions
            final_preds = np.array([np.mean(aggregated_preds[idx]) for idx in range(len(y))])

            pearson_corr, pvalue = pearsonr(y, final_preds)

            fw_result.write(
                f"{meta}\t"
                f"{pearson_corr:.4f}\t"
                f"{pvalue}\n"
            )
            fw_result.flush()
        fw_result.flush()
        fw_result.close()