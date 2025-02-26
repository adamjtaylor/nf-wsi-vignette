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

# qc_mask_path = sys.argv[4]
#
# # Load the mask and find the tissue region
# qc_mask = cv2.imread(qc_mask_path, cv2.IMREAD_GRAYSCALE)
#
# # Tissue region is where the mask is not 7
# tissue_region = np.where(qc_mask != 7)
#
# # Mask is at 1.5 mpp resolution
# qc_mask_mpp = 1.5
#
# # we need to scale this to match the resolution of the WSI
# # we will use the WSIReader to get the resolution of the WSI
# wsi_reader = WSIReader(wsi_path)
# wsi_mpp = wsi_reader.mpp
# scale_factor = wsi_mpp / qc_mask_mpp
#
# # Scale the tissue region so it has the same dimensions as the WSI
# new_shape = (
#     int(tissue_region.shape[1] * scale_factor),
#     int(tissue_region.shape[0] * scale_factor),
# )
#
# # Resize using OpenCV
# tissue_region_scaled = cv2.resize(
#     tissue_region, new_shape, interpolation=cv2.INTER_LINEAR
# )

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
    auto_generate_mask=True,
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
    out = extractor.predict(
        imgs=[wsi_path],
        mode="wsi",
        ioconfig=wsi_ioconfig,
        save_dir=str(save_dir),  # Ensure it's a string
        device=device,
    )

    print("Feature extraction completed")
