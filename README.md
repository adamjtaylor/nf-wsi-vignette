# nf-wsi-vignette

A Nextflow pipeline for analyzing Whole Slide Images (WSI) using GrandQC and foundation models.

## Overview

This pipeline provides automated analysis of whole slide images using:

- GrandQC for quality control and artifact detection
- Foundation model embeddings for tissue analysis
- TIA Toolbox for image processing and analysis

## Requirements

- Nextflow
- Conda/Mamba
- Python 3.10+
- A HuggingFace token
- Approved access for the relevent model on HuggingFace

## Installation

1. Clone this repository
2. Create and activate the conda environments:

```bash
# Create GrandQC environment
conda env create -f conda/grand_qc.yml

# Create TIA Toolbox environment 
conda env create -f conda/tiatoolbox.yml
```

## Usage

Run the pipeline using:

```
nextflow run main.nf \
    --samplesheet test_data/small.csv \
    -profile conda,local \
    --grand_qc true \
    --foundation true
```

# Parameters

- `samplesheet`: Path to the samplesheet
- `outdir`: Path to the output directory
- `grandqc`: Should GrandQC be run (default: true)
- `foundation`: Should the foundation model be run - (default: false)
- `foundation_model`: Which foundation model should - be used (default: 'H-Optimus-0', other models not - tested)
- `huggingface_hub_pat`: Path to your HuggingFace cache

## Workflows

- `grand_qc.nf` - GrandQC workflow
- `tia_toolbox.nf` - TIA Toolbox processing steps
modules - Individual process modules

## Modules
- `grand_qc_run.nf` - GrandQC execution
- `grand_qc_metrics.nf` - Extraction of artefact metrics from GrandQC QC mask
- `grand_qc_report` - Generate a markdown report from GrandQC outputs
- `foundation_model_embedding.nf` - Tile embedding with a pathology foundation model
- `foundation_model_clustering.nf` - Clustering of tiles based on embedding vectors and selection of representative tiles

## Outputs
The pipeline generates:

- Tissue detection masks
- Artifact detection overlays
- QC metrics and reports
- Foundation model embeddings
- Clustering results