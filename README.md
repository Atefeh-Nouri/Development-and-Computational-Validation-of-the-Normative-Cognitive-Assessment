@'
# Normative Cognitive Assessment Database (NCAD) Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)

## Overview
This repository provides the computational architecture and psychometric modeling pipelines for the **Normative Cognitive Assessment Database (NCAD)** project. 

The pipeline fits **Linear Mixed-Effects Models (LMM)** and calculates **Signal Detection Theory (SDT)** parameters to evaluate developmental trajectories across executive functions (visuospatial working memory, response inhibition, sustained attention, and processing speed) in adolescents aged 12–18.

## Open Science & Data Privacy Notice
In accordance with international pediatric and adolescent data protection standards (**GDPR / institutional ethics**), this public repository demonstrates the pipeline using an empirically calibrated benchmark dataset ($N = 2,000$). The benchmark mirrors the exact covariance matrices and variance distributions of the adolescent cohort without exposing individual identifiable records.

## Repository Structure
```text
├── dataset/
│   └── NCAD_Iranian_Dataset.xlsx          # Benchmark dataset (N=2,000)
├── src/
│   ├── 01_data_validation.py              # Stratification analysis & Table 1
│   └── 02_lmm_modeling.py                 # LMM fitting, Table 2 & trajectory plots
├── results/
│   ├── tables/                            # Output CSV tables
│   └── figures/                           # High-resolution PNG plots
├── requirements.txt                       # Python dependencies
└── README.md