import polars as pl


def find_n_top_variance(data_path: str, N: int, max_missing: float) -> pl.DataFrame:
    df = pl.read_csv(data_path, separator="\t", infer_schema_length=0, null_values="NA")

    df_with_stats = df.with_columns(
        (
            pl.concat_list(pl.all().exclude("analyte"))
            .list.eval(pl.element().null_count())
            .flatten()
            / df.width
        ).alias("missing_percent")
    )
    df_with_stats = df_with_stats.with_columns(
        [
            # Compute variance while ignoring missing values
            pl.concat_list(pl.all().exclude("analyte").cast(pl.Float64))
            .list.var()
            .alias("variance"),
        ]
    )
    filtered_df = df_with_stats.filter(
        pl.col("missing_percent").le(pl.lit(max_missing))
    )

    # Select the top N rows with the highest variance
    top_n_rows = (
        filtered_df.sort("variance", descending=True)
        .head(N)
        .select(["analyte", "variance"])
    )
    return top_n_rows
