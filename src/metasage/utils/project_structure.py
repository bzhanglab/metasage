import os
from rich.tree import Tree
from rich import print
from pathlib import Path

PATHS = ["data", "output", "data/host", "data/extra_features"]
BASE_CONFIG = """analyte_list = "" # path single column list of PTM sites to build models for
modifier_list = "" # path single column list of PTM modifiers to include features of
keep_features = [""] # List of features to keep regardless of filter criteria (See documentation for feature naming conventions)
remove_features = [""] # List of features to remove regardless of filter criteria (See documentation for feature naming conventions)
only_use_listed_data = false # use only listed data files. If false, will use all TSV (*.tsv) files in the data/ folder
site_separator = "|" # Character used to separate the gene from the site (ex: ABC1|K234)
filter_by_ppi = true # filter the modifier lists by removing proteins not known to have PPI with the host protein of interest
do_feature_selection = false # whether to perform feature selection (independent of ppi filtering)

[params]
max_na_ratio = 0.1 # Max ratio of missing values allowed in a feature

[[data]] # optional list of [[data]] if you need to specify
path = "host/example.tsv" # Path to data file (path relative to data folder)
ignore_cols = [""] # List of columns to ignore in file (e.g. multiple ID columns)
# name = "Custom Name" # Optional name for dataset. If not set, defaults to path without file extension (example)
"""


def create_project_structure(base_path: str, force: bool) -> None:
    print("")
    print("🏗️ Creating project structure")
    base_path: Path = Path(base_path)
    for project_path in PATHS:
        new_path = Path.joinpath(base_path, project_path)
        if not os.path.exists(new_path):
            print(f"[grey84]    Creating path at {new_path}[/grey84]")
            os.makedirs(new_path)

    # Tree building
    main_tree = Tree(str(base_path))
    data_tree = main_tree.add("data")
    host_tree = data_tree.add("host")
    host_tree.add("[blue]Input data for host protein info (protein, RNA, etc.)[/blue]")
    extra_feat = data_tree.add("extra_features")
    extra_feat.add("[blue]Input data extra features used for PTM modifiers[/blue]")
    output_tree = main_tree.add("output")
    output_tree.add("[blue]Output from the models[/blue]")
    print("")
    print(main_tree)
    print("")

    # Create config.toml
    config_path = base_path.joinpath("config.toml")
    if not os.path.exists(config_path) or force:
        print(f"[bold]Creating config at {config_path}[/bold]")
        with open(config_path, "w") as w:
            w.write(BASE_CONFIG)
