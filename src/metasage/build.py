from metasage.config import Config
from metasage.utils.messages import print_info
from metasage.utils.read import read_data_file_to_dataframe
import polars as pl
import os
from sklearn.cluster import AgglomerativeClustering
import numpy as np


class GeneCluster:
    def __init__(self):
        self.clusters = []

    def add_gene(self, gene: str):
        for cluster in self.clusters:
            if gene in cluster:
                return
        self.clusters.append({gene})

    def merge_clusters(self, gene1: str, gene2: str):
        cluster1 = cluster2 = None
        for cluster in self.clusters:
            if gene1 in cluster:
                cluster1 = cluster
            if gene2 in cluster:
                cluster2 = cluster
        if cluster1 and cluster2 and cluster1 != cluster2:
            cluster1.update(cluster2)
            self.clusters.remove(cluster2)

    def get_clusters(self):
        return self.clusters


def cluster_ppi_genes(host: str, ppi_data_path: str = "all_ppi.tsv") -> list[set[str]]:
    with open(ppi_data_path) as r:
        lines = r.read().split("\n")
    valid_genes = set()
    gene_pairs = []
    for line in lines:
        if "\t" in line:
            vals = line.split("\t")
            if vals[0] == host:
                valid_genes.add(vals[1])
            elif vals[1] == host:
                valid_genes.add(vals[0])
            gene_pairs.append((vals[0], vals[1]))

    gene_list = list(valid_genes)
    gene_index = {gene: idx for idx, gene in enumerate(gene_list)}

    adjacency_matrix = np.zeros((len(gene_list), len(gene_list)))
    for gene1, gene2 in gene_pairs:
        if gene1 in gene_index and gene2 in gene_index:
            idx1, idx2 = gene_index[gene1], gene_index[gene2]
            adjacency_matrix[idx1, idx2] = 1
            adjacency_matrix[idx2, idx1] = 1

    clustering = AgglomerativeClustering(
        linkage="complete",
        n_clusters=10,
        # distance_threshold=0,
    ).fit(1 - adjacency_matrix)

    clusters = {}
    for gene, label in zip(gene_list, clustering.labels_):
        if label not in clusters:
            clusters[label] = set()
        clusters[label].add(gene)

    return list(clusters.values())


def ppi_genes(host: str, ppi_data_path: str = "all_ppi.tsv") -> set[str]:
    with open(ppi_data_path) as r:
        lines = r.read().split("\n")
    genes = set()
    for line in lines:
        if "\t" in line:
            vals = line.split("\t")
            if vals[0] == host:
                genes.add(vals[1])
            elif vals[1] == host:
                genes.add(vals[0])
    return genes


def extract_base_gene(gene: str, separator="|") -> str:
    """Extract the base gene name before '|SiteX'."""
    return gene.split(separator)[0]  # Extracts 'Gene' from 'Gene_Site1'


def load_expression_data(file_path: str, gene_list: set) -> pl.DataFrame:
    """load a single data set, and create feature matrix

    Args:
        file_path (str): path the data set (TSV only)
        gene_list (set): set of genes that you are creating features for

    Raises:
        ValueError: raised if the id column is not found

    Returns:
        pl.DataFrame: Polars DataFrame with the first column being the Sample and columns in format of Gene_FileName
    """

    """Load and filter a gene expression file based on target genes."""
    file_name = os.path.basename(file_path).replace(".tsv", "")

    # Read the file
    df = pl.read_csv(file_path, separator="\t", infer_schema_length=0, null_values="NA")
    id_col = df.columns[0]  # ID column is the first column

    # Extract base gene names
    df = df.with_columns(pl.col(id_col).alias("Original_Analyte"))  # Preserve original
    df = df.with_columns(
        pl.col(id_col)
        .map_elements(extract_base_gene, return_dtype=pl.String)
        .alias("Base_Analyte")
    )

    # Filter: Keep rows where Base_Gene is in the gene_list
    df_filtered = df.filter(pl.col("Base_Analyte").is_in(gene_list)).drop(
        "Base_Analyte", "analyte"
    )
    # Convert to long format (Sample, Gene_SiteX, Value)
    df_long = df_filtered.unpivot(
        index=["Original_Analyte"], variable_name="Sample", value_name="Value"
    )

    # Rename feature columns to include the file name
    df_long = df_long.with_columns(
        (pl.col("Original_Analyte") + "_" + file_name).alias("Feature")
    ).select(["Sample", "Feature", "Value"])
    df_long = df_long.with_columns(pl.col("Value").cast(pl.Float64))
    return df_long


def merge_expression_data(file_paths: list, gene_list: set) -> pl.DataFrame:
    """Merge multiple expression data files into a single matrix."""
    all_data = [load_expression_data(fp, gene_list) for fp in file_paths]
    # Concatenate and pivot into wide format
    final_df = pl.concat(all_data).pivot(
        index="Sample", on="Feature", values="Value", aggregate_function="last"
    )

    return final_df


def feature_selection(
    df: pl.DataFrame, var_threshold: float = 0.01, missing_threshold: float = 0.2
) -> pl.DataFrame:
    """
    Apply feature selection:
    - Remove features with low variance.
    - Remove features with excessive missing values.
    """
    # Compute variance

    # Extract the first column name (assumed to be sample identifier)
    first_col = df.columns[0]

    # Compute variance for all columns except the first
    feature_variance = df.select(pl.all().exclude(first_col).var(ddof=1)).to_dict(
        as_series=True
    )

    # Compute missing value ratio correctly for all columns except the first
    missing_ratio = df.select(
        (pl.all().exclude(first_col).null_count() / df.height)
    ).to_dict(as_series=True)

    # Select features that meet both thresholds
    selected_features = [
        k
        for k in feature_variance.keys()
        if feature_variance[k].item() is not None
        and feature_variance[k].item() > var_threshold
        and missing_ratio[k].item() < missing_threshold
    ]

    # Keep only the first column and selected features
    return df.select([first_col] + selected_features)


def get_host_cols(
    feature_df: pl.DataFrame,
    gs_file: str,
    files: list[str],
    site: str,
    site_separator: str = "|",
    only_label: bool = False,
):
    gs_df = read_data_file_to_dataframe(gs_file)
    base_gene = extract_base_gene(
        site, separator=site_separator
    )  # TODO: Add separator from config
    gs_df = (
        gs_df.filter(pl.col("analyte").eq(pl.lit(site)))
        .unique(subset="analyte", keep="last")
        .drop("analyte")
    )
    gs_df = gs_df.transpose(
        include_header=True, header_name="Sample", column_names=["label"]
    )
    if only_label:
        return gs_df
    host_dfs: list[pl.DataFrame] = []
    for file in files:
        df = read_data_file_to_dataframe(file)
        file_name = os.path.basename(file).split(".")[0]
        df = df.filter(pl.col("analyte").eq(pl.lit(base_gene))).drop("analyte")
        host_dfs.append(
            df.transpose(
                include_header=True,
                header_name="Sample",
                column_names=[f"host_{file_name}"],
            )
        )
    host_dfs.append(gs_df)
    df_main = host_dfs[0]
    for i in range(1, len(host_dfs)):
        df_main = df_main.join(host_dfs[i], on="Sample", how="full", coalesce=True)
    return df_main


# def add_feature_from_file(File: DataFileConfig, modifiers: list[str]):
#     pass


def build(config: Config):
    print("""
🛠️ Building Feature Matrix
""")
    modifier_path = config.modifier_list
    with open(modifier_path) as r:
        modifiers = r.read().split("\n")
        modifiers = [m.strip() for m in modifiers if m.strip()]  # remove blank lines
    modifiers = set(modifiers)

    print_info(f"Identified {len(modifiers)} PTM modifiers")

    # for file in config.data_files:
    #     add_feature_from_file(file, modifiers)
