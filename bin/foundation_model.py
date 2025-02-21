import logging
import warnings
from pathlib import Path
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import umap
from huggingface_hub import notebook_login

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
"""
'cuda:0' - NVIDIA GPU card
'mps'    - APPLE Silicon
'cpu'    - Default to CPU if no GPU is available
"""

# File name of WSI
wsi_path = sys.argv[1]

notebook_login()

model = TimmBackbone(backbone="H-optimus-0", pretrained=True)

wsi_ioconfig = IOSegmentorConfig(
    input_resolutions=[{"units": "mpp", "resolution": 0.5}],
    patch_input_shape=[224, 224],
    output_resolutions=[{"units": "mpp", "resolution": 0.5}],
    patch_output_shape=[224, 224],
    stride_shape=[224, 224],
)

# create the feature extractor and run it on the WSI
extractor = DeepFeatureExtractor(
    model=model,
    auto_generate_mask=True,
    batch_size=32,
    num_loader_workers=4,
    num_postproc_workers=4,
)

out = extractor.predict(
    imgs=[wsi_path],
    mode="wsi",
    ioconfig=wsi_ioconfig,
    save_dir="wsi_features",
    device=device,
)
