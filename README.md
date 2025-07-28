# MetaSage

Use `xgboost` to predict metabolites abundance, and use importance scores to determine metabolites and enzymes important for prediction.

## Installation

Install from this repository using the below command

```shell
pip install git+https://github.com/bzhanglab/metasage
```

For help, run `metasage --help`

## Usage

To initialize a project in your current directory run

```shell
metasage init .
```

This will create the project folder structure, as well as an example config file located at `config.toml`. Modify this config to match your project.

To build the modifier feature matrix, run 

```shell
metasage build
```

## Citation

```
MetaSage: Machine Learning-Based Prioritization of Metabolic Regulators from Multi-Omics Data
Chenwei Wang, John M. Elizarraras, Bing Zhang
```