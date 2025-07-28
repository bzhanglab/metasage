import polars as pl


def read_data_file_to_dataframe(file_path: str) -> pl.DataFrame:
    df = pl.read_csv(file_path, separator="\t", infer_schema_length=0, null_values="NA")
    first_col = df.columns[0]
    return df.with_columns(pl.all().exclude(first_col).cast(pl.Float64))
