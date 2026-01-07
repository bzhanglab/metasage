import os
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
import shap

def prioritizatioin():
    path = "~/feature/"
    output_path = "~/regulator_prioritization/"
    os.makedirs(output_path, exist_ok=True)

    for item in os.listdir(path):
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
        if X.shape[1] == 0:
            print(f"Skipping {item} - No valid features after dropping 'meta'")
            continue
        model = xgb.XGBRegressor(n_estimators=100, random_state=1)
        model.fit(X, y)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        shap_mean_abs = pd.DataFrame({
            'Feature': X.columns,
            'MeanAbsSHAP': pd.Series(abs(shap_values).mean(axis=0))
        }).sort_values(by='MeanAbsSHAP', ascending=False).reset_index(drop=True)

        shap_mean_abs.to_csv(os.path.join(output_path, f"{meta}.tsv"), sep="\t", index=False)

        plt.figure(figsize=(4, 4))
        shap.summary_plot(shap_values, X, show=False)
        plt.savefig(os.path.join(output_path, f"{meta}.pdf"), bbox_inches='tight')
        plt.close()

        print(f"Processed and saved results for {meta}")





