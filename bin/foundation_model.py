#!/usr/bin/env python
print("Importing libraries")
import logging
import warnings
from pathlib import Path
import sys
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import umap
from huggingface_hub import login
import torch
from tiatoolbox import logger
from tiatoolbox.models.architecture.vanilla import TimmBackbone
from tiatoolbox.models.engine.semantic_segmentor import (
    DeepFeatureExtractor,
    IOSegmentorConfig,
)
from tiatoolbox.utils.misc import download_data
from tiatoolbox.wsicore.wsireader import WSIReader

# Configure logging and warnings
if logging.getLogger().hasHandlers():
    logging.getLogger().handlers.clear()
warnings.filterwarnings("ignore", message=".*The 'nopython' keyword.*")

# Configure matplotlib
mpl.rcParams["figure.dpi"] = 300  # for high resolution figure in notebook
mpl.rcParams["figure.facecolor"] = "white"  # To make sure text is visible in dark mode

device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available() else "cpu"
)

if device == "mps":
    import multiprocessing

    multiprocessing.set_start_method("spawn", force=True)

"""
'cuda:0' - NVIDIA GPU card
'mps'    - APPLE Silicon
'cpu'    - Default to CPU if no GPU is available
"""

# File name of WSI
wsi_path = sys.argv[1]
model_dir = sys.argv[2]


print(f"WSI Path: {wsi_path}")
print(f"Device: {device}")

print("Logging into Hugging Face Hub")
login("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")


os.environ["HF_HOME"] = model_dir

print("Downloading the model")
model = TimmBackbone(backbone="H-optimus-0", pretrained=True)

print("Creating the WSI IO config")
wsi_ioconfig = IOSegmentorConfig(
    input_resolutions=[{"units": "mpp", "resolution": 0.5}],
    patch_input_shape=[224, 224],
    output_resolutions=[{"units": "mpp", "resolution": 0.5}],
    patch_output_shape=[224, 224],
    stride_shape=[224, 224],
)

# create the feature extractor and run it on the WSI
print("Creating the feature extractor")
extractor = DeepFeatureExtractor(
    model=model,
    auto_generate_mask=True,
    batch_size=32,
    num_loader_workers=4,
    num_postproc_workers=4,
)

# Ensure save_dir exists or clean it up
save_dir = Path("wsi_features")
if save_dir.exists():
    print(f"Reusing existing directory: {save_dir}")

if __name__ == "__main__":

    # Run the feature extractor
    print("Running the feature extractor")
    out = extractor.predict(
        imgs=[wsi_path],
        mode="wsi",
        ioconfig=wsi_ioconfig,
        save_dir=str(save_dir),  # Ensure it's a string
        device=device,
    )

    print("Feature extraction completed")
