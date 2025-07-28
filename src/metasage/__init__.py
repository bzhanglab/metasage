import typer
import glob
import polars as pl
from metasage.build import (
    cluster_ppi_genes,
    extract_base_gene,
    merge_expression_data,
    feature_selection,
    get_host_cols,
    ppi_genes,
)
from metasage.config import load_config_from_toml
from metasage.train import (
    TooManyMissingSite,
    model_result_to_dict,
    process_site,
    train_model,
)
from metasage.utils.max_variance import find_n_top_variance
from metasage.utils.plot import plot_x_y
from metasage.utils.project_structure import create_project_structure
import json
from rich.progress import track

app = typer.Typer(pretty_exceptions_enable=False)


@app.command("init")
def init(
    base_path: str,
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force creation of project even if some files already exist.",
    ),
) -> None:
    create_project_structure(base_path, force)


@app.command("build")
def build(config="config.toml"):
    load_config_from_toml(config)


@app.command("plot")
def plot(x: str, y: str):
    x_file = x.split("_")[1] + ".tsv"
    y_file = y.split("_")[1] + ".tsv"
    plot_x_y(x, x_file, y, y_file)


@app.command("max_variance")
def max_variance(data_path, n=50, max_missing=0.2):
    df = find_n_top_variance(data_path, int(n), float(max_missing))
    df.write_csv("variance.tsv", separator="\t")
    print(df.head())


@app.command("fix")
def fix():
    # TODO: Remove
    all_files = list(glob.glob("*.tsv"))
    for file in all_files:
        if "prot" in file.lower() or "rna" in file.lower():
            continue
        with open(file) as r:
            text = r.read().replace("_", "|")
        with open(file, "w") as w:
            w.write(text)


@app.command("train")
def train(z: bool = False):
    train_model(use_z=z)


@app.command("host")
def host(site: str, only_label: bool = False):
    base_gene = extract_base_gene(site)
    host_df = get_host_cols(
        None,
        "phospho.tsv",
        ["rna.tsv", "protein.tsv"],
        site,
        "|",
        only_label=only_label,
    )
    df = pl.read_parquet("common_features.parquet")
    valid_features = ppi_genes(base_gene)
    columns_to_keep = ["Sample"]

    for col in df.columns:
        check_col = col.removesuffix("_protein")
        check_col = check_col.removesuffix("_rna")
        # Check if column's base gene is in valid_features
        if extract_base_gene(check_col) in valid_features:
            columns_to_keep.append(col)
    df = df.select(columns_to_keep)
    df = df.select(
        [
            col
            for col in df.columns
            if col != f"{site}_phospho"
            and not col.startswith(f"{base_gene}_rna")
            and not col.startswith(f"{base_gene}_protein")
        ]
    )
    df = df.join(host_df, on="Sample", how="full", coalesce=True)
    print(df.head())
    df.write_parquet("data.parquet")


@app.command("test")
def test(reduce: bool = False):
    blacklist = ["common_features.tsv", "variance.tsv", "all_ppi.tsv"]
    all_files = list(glob.glob("*.tsv"))
    all_files = [file for file in all_files if file not in blacklist]
    modifier_path = "modifiers.txt"
    with open(modifier_path) as r:
        modifiers = r.read().split("\n")
        modifiers = [m.strip() for m in modifiers if m.strip()]  # remove blank lines
    merged_df = merge_expression_data(all_files, modifiers)
    print(merged_df.shape)
    if reduce:
        merged_df = feature_selection(
            merged_df, missing_threshold=0.5, var_threshold=0.05
        )
        print("-----------")
        print(merged_df.shape)
    merged_df.write_parquet("common_features.parquet")
    merged_df.write_csv("common_features.tsv", separator="\t")


@app.command("start")
def start(name: str) -> None:
    print(f"Hello {name}")


@app.command("full")
def full(
    site_list: str, runs: int = 1, fixed: bool = False, only_label: bool = False
) -> None:
    with open(site_list, "r") as r:
        text = r.read()
    lines = text.split("\n")
    sites = [line.strip() for line in lines if line.strip()]
    blacklist = ["common_features.tsv", "variance.tsv", "all_ppi.tsv"]
    all_files = list(glob.glob("*.tsv"))
    all_files = [file for file in all_files if file not in blacklist]
    modifier_path = "modifiers.txt"
    with open(modifier_path) as r:
        modifiers = r.read().split("\n")
        modifiers = [m.strip() for m in modifiers if m.strip()]  # remove blank lines
    merged_df = merge_expression_data(all_files, set(modifiers))

    model_results = []
    for site in track(sites):
        try:
            res = process_site(
                site, merged_df, fixed_seed=fixed, runs=runs, only_label=only_label
            )
            model_results.append(res)
        except TooManyMissingSite:
            print(f"{site} has too many NA")
        except:
            print(f"Could not process {site}")
    result_dict = [model_result_to_dict(res) for res in model_results]
    with open("results.json", "w") as w:
        json.dump(result_dict, w)
    print("Done processing")


def main() -> None:
    app()
