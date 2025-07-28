import tomllib
from typing import Any
from rich import print, print_json
import sys

from metasage.utils.messages import print_error


class ConfigParams:
    max_na_ratio: float

    def __init__(self, max_na_ratio=0.1):
        self.max_na_ratio = max_na_ratio


class DataFileConfig:
    path: str
    ignore_cols: list[str]
    is_host: bool

    def __init__(self, path, ignore_cols=[], is_host=None):
        self.path = path
        self.ignore_cols = ignore_cols
        if is_host is None:
            self.is_host = "extra_features/" not in path
        else:
            self.is_host = is_host


class Config:
    analyte_list: str
    modifier_list: str
    keep_features: list[str]
    remove_features: list[str]
    params: ConfigParams
    only_use_listed_data: bool
    data_files = list[DataFileConfig]
    site_separator = str
    filter_by_ppi: bool
    do_feature_reduction: bool

    def __init__(
        self,
        analyte_list,
        modifier_list,
        keep_features=[],
        remove_features=[],
        site_separator="|",
        params=ConfigParams(),
        data_files=[],
        only_use_listed_data=False,
        filter_by_ppi: bool = True,
        do_feature_reduction: bool = False,
    ):
        self.analyte_list = analyte_list
        self.modifier_list = modifier_list
        self.keep_features = keep_features
        self.site_separator = "|"
        self.remove_features = remove_features
        self.params = params
        self.data_files = data_files
        self.only_use_listed_data = only_use_listed_data
        self.filter_by_ppi = filter_by_ppi
        self.do_feature_reduction = do_feature_reduction

    def add_data_file(self, data_file: DataFileConfig) -> None:
        self.data_files.append(data_file)


def check_required_key(config_toml: dict, key: str) -> None:
    if key not in config_toml:
        print_error(f"Missing key [yellow]{key}[/yellow] from config")
        print("\nConfig:")
        print_json(data=config_toml)
        sys.exit(1)


def check_type(key: str, obj_type: Any, config_toml: dict) -> None:
    if not isinstance(config_toml[key], obj_type):
        print_error(
            f"[yellow]{key}[/yellow] should of type [yellow]{obj_type}[/yellow].\n\n\tCurrent Type: [yellow]{type(config_toml[key]).__name__}[/yellow]\n\tCurrent Value: {config_toml[key]}"
        )
        print("\nConfig:")
        print_json(data=config_toml)
        sys.exit(1)


def check_and_set(
    config: Config | ConfigParams, toml_obj: dict, attr: str, attr_type: Any
) -> None:
    if attr in toml_obj:
        check_type(attr, attr_type, toml_obj)
        setattr(config, attr, toml_obj[attr])


def load_config_from_toml(config_path: str) -> Config:
    print("")
    print(f"[blue]Loading config from {config_path}[/blue]")
    with open(config_path, "rb") as r:
        config_toml = tomllib.load(r)
    required_keys = ["analyte_list", "modifier_list"]
    for key in required_keys:
        check_required_key(config_toml, key)
    config = Config(
        analyte_list=config_toml["analyte_list"],
        modifier_list=config_toml["modifier_list"],
    )
    to_check = [
        ("keep_features", list),
        ("remove_features", list),
        ("only_use_listed_data", bool),
        ("filter_by_ppi", bool),
        ("do_feature_selection", bool),
        ("site_separator", str),
    ]
    for attr, attr_type in to_check:
        check_and_set(config, config_toml, attr, attr_type)
    if "params" in config_toml:
        params_toml = config_toml["params"]
        check_and_set(config.params, params_toml, "max_na_ratio", float)
    data_files: list[DataFileConfig] = []
    processed_files = set()
    if "data" in config_toml:
        required_keys = ["path"]
        for data_file_toml in config_toml["data"]:
            for key in required_keys:
                check_required_key(data_file_toml, key)
            data_file = DataFileConfig(data_file_toml["path"])
            if "ignore_cols" in data_file_toml:
                check_type("ignore_cols", list, data_file_toml)
                data_file.ignore_cols = data_file_toml["ignore_cols"]
            if "is_host" in data_file_toml:
                check_type("is_host", bool, data_file_toml)
                data_file.is_host = data_file_toml["is_host"]
            data_files.append(data_file)
            processed_files.add(data_file_toml["path"])
    return config
