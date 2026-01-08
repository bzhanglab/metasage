# MetaSage

A machine learning–based framework designed to systematically infer regulatory mechanisms underlying metabolic dysregulation in different conditions

## Usage

3 python scripts were included to match the 3 major steps of MetaSage:

```shell
Feature_generation.py
```

This script was used to create the input file of each metabolite for downstream model training. The output file will contain the abundances of specific metabolite, and the features extracted from preprapred file:
  gene_expression_file: gene expression matrix from omics data, eg RNASeq or proteomic. The first row should be the samples IDs and the first column should be the gene symbols. An example file is included in "Example_files" folder.
  metabolite_expression_file: metabolite expression matrix from metabolomic data. The first row should be the samples IDs and the first column should be the unified metabolite names. An example file is included in "Example_files" folder.
  meta_gene_relation_file: for each target metabolite, it's quantified associated genes and upstream reactants were curated from the known GEM and filtered based on the study-specific multi-omics datasets. An example file is included in "Example_files" folder.
  ESTIMATE_score_results: matrix containing 4 infered scores from ESTIMATE, including stromal score, immune score, ESTIMATE score and tumor purity. An example file is included in "Example_files" folder.

```shell
metasage build
```

## Citation

```
MetaSage: Machine Learning-Based Prioritization of Metabolic Regulators from Multi-Omics Data
Chenwei Wang, John M. Elizarraras, Bing Zhang
```
