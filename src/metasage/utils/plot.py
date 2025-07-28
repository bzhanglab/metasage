from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import polars as pl
import pandas as pd
from metasage.utils.read import read_data_file_to_dataframe


def plot_x_y(x: str, x_file: str, y: str, y_file):
    sns.set_theme(context="paper", style="white")
    clean_x = x.split("_")[0]
    x_df = read_data_file_to_dataframe(x_file)
    x_data = (
        x_df.filter(pl.col("analyte").eq(pl.lit(clean_x)))
        .drop("analyte")
        .row(0, named=True)
    )
    clean_y = y.split("_")[0]
    y_df = read_data_file_to_dataframe(y_file)
    y_data = (
        y_df.filter(pl.col("analyte").eq(pl.lit(clean_y)))
        .drop("analyte")
        .row(0, named=True)
    )

    # Create DataFrame from the dictionaries
    df = pd.DataFrame(
        {"x": list(x_data.values()), "y": list(y_data.values())},
        index=list(x_data.keys()),
    )
    df["category"] = [
        "Normal" if str(idx).endswith(".N") else "Tumor" for idx in df.index
    ]

    lin = df.dropna(how="any")

    # Calculate the linear regression and get statistics
    slope, intercept, r_value, p_value, std_err = stats.linregress(lin["x"], lin["y"])
    plt.close()
    # Create the figure and plot
    plt.figure(figsize=(10, 6))
    ax = sns.lmplot(
        x="x",
        y="y",
        data=df,
        hue="category",
        legend_out=True,
        # scatter_kws={"s": 80, "alpha": 0.7},
        # line_kws={"color": "red"},
    )

    # Add a title and labels
    plt.title("", fontsize=16)
    plt.xlabel(x, fontsize=12)
    plt.ylabel(y, fontsize=12)

    # Add text annotation with the regression information
    equation = f"y = {slope:.3f}x + {intercept:.3f}"
    r_squared = f"R² = {r_value**2:.3f}"
    plt.annotate(
        f"{equation}\n{r_squared}",
        xy=(0.05, 0.95),
        xycoords="axes fraction",
        fontsize=12,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.7),
    )

    # Show grid
    plt.grid(True, linestyle="--", alpha=0.7)

    # # Optional: Add point labels
    # for i, txt in enumerate(df.index):
    #     plt.annotate(
    #         txt,
    #         (df["x"].iloc[i], df["y"].iloc[i]),
    #         xytext=(5, 5),
    #         textcoords="offset points",
    #     )

    plt.tight_layout()
    plt.show()
