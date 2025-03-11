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
import cv2

# import cv2

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
# model_dir = "/Users/ataylor/.cache/huggingface"
model = sys.argv[3]

# Load the QC mask with unchanged bit depth
qc_mask_path = sys.argv[4]

# if qc_mask_path is not null
use_qc_mask = sys.argv[5].lower() in ('true', 't', 'yes', 'y', '1')
print(f"Use QC Mask: {use_qc_mask}")
if use_qc_mask:

    qc_mask = cv2.imread(qc_mask_path, cv2.IMREAD_UNCHANGED)

    # Ensure the mask only has values 0-7
    if qc_mask.max() > 7:
        raise ValueError("Mask should have values between 0 and 7")

    # Convert to an 8-bit binary mask (255 for tissue, 0 for background)
    tissue_region = np.where(qc_mask == 1, 255, 0).astype(np.uint8)

    # Save as an 8-bit grayscale PNG
    tissue_region_path = Path("tissue_region.png")
    cv2.imwrite(str(tissue_region_path), tissue_region)


# if the model is prov-gigapath then patch shape is 256x256
if model == "Prov-GigaPath":
    patch_shape = [256, 256]
else:
    patch_shape = [224, 224]

print(f"WSI Path: {wsi_path}")
print(f"Device: {device}")


# Set the Hugging Face Home directory
os.environ["HF_HOME"] = model_dir

# Login to Hugging Face
login(os.getenv("HF_TOKEN"))

print("Downloading the model")
model = TimmBackbone(backbone=model, pretrained=True)

print("Creating the WSI IO config")
wsi_ioconfig = IOSegmentorConfig(
    input_resolutions=[{"units": "mpp", "resolution": 0.5}],
    patch_input_shape=patch_shape,
    output_resolutions=[{"units": "mpp", "resolution": 0.5}],
    patch_output_shape=patch_shape,
    stride_shape=patch_shape,
)

# create the feature extractor and run it on the WSI
print("Creating the feature extractor")
extractor = DeepFeatureExtractor(
    model=model,
    auto_generate_mask=False if use_qc_mask else True,
    batch_size=32,
    num_loader_workers=3,
    num_postproc_workers=3,
)

# Ensure save_dir exists or clean it up
save_dir = Path("wsi_features")
if save_dir.exists():
    print(f"Reusing existing directory: {save_dir}")

if __name__ == "__main__":

    # Run the feature extractor
    print("Running the feature extractor")
    if use_qc_mask:
        out = extractor.predict(
            imgs=[wsi_path],
            masks=[tissue_region_path],
            mode="wsi",
            ioconfig=wsi_ioconfig,
            save_dir=str(save_dir),  # Ensure it's a string
            device=device,
        )
    else:
        out = extractor.predict(
            imgs=[wsi_path],
            mode="wsi",
            ioconfig=wsi_ioconfig,
            save_dir=str(save_dir),  # Ensure it's a string
            device=device,
        )
    print("Feature extraction completed")