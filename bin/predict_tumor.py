#!/usr/bin/env python

import shutil
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys
import torch

from tiatoolbox import logger
from tiatoolbox.models.engine.patch_predictor import PatchPredictor
from tiatoolbox.utils.misc import imwrite
from tiatoolbox.utils.visualization import (
    overlay_prediction_mask,
    overlay_probability_map,
)
from tiatoolbox.wsicore.wsireader import WSIReader

from pathlib import Path

wsi_path = sys.argv[1]

device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available() else "cpu"
)

if device == "mps":
    import multiprocessing

    multiprocessing.set_start_method("spawn", force=True)


tumour_predictor = PatchPredictor(
    pretrained_model="resnet18-idars-tumour",
    batch_size=64,
    num_loader_workers=0,
)

tumour_output = tumour_predictor.predict(
    imgs=[Path(wsi_path)],
    mode="wsi",
    return_probabilities=True,
    device=device,
)

# The resolution in which we desire to merge and visualize the patch predictions
overview_resolution = 1.25
# The unit of the `resolution` parameter.
# Possible values are "power", "level", "mpp", or "baseline".
overview_unit = "power"

# merge predictions to form a 2-dimensional output at the desired resolution
tumour_mask = tumour_predictor.merge_predictions(
    wsi_path,
    tumour_output[0],
    resolution=overview_resolution,
    units=overview_unit,
)

# the output map will contain values from 0 to 2.
# 0:background that is not processed, 1:non-tumour prediction, 2:tumour predictions
tumour_mask = tumour_mask == 2  # binarise the output  # noqa: PLR2004

# let's save the tumour mask, so that we can use it in stage 2!
imwrite("tumour_mask.png", tumour_mask.astype("uint8") * 255)

# first read the WSI at a low-resolution.
# Here, we use the same resolution that was used when merging the patch-level results.
wsi = WSIReader.open(wsi_path)
wsi_overview = wsi.slide_thumbnail(resolution=overview_resolution, units=overview_unit)

# [Overlay map creation]
# Creating label-color dictionary to be fed into `overlay_prediction_mask` function
# This helps to generate a color legend.
label_dict = {"Non-Tumour": 0, "Tumour": 1}
label_color_dict = {}
colors = [[255, 255, 255], [255, 0, 0]]  # defining colours for overlay (white and red)
for class_name, label in label_dict.items():
    label_color_dict[label] = (class_name, np.array(colors[label]))

overlay = overlay_prediction_mask(
    wsi_overview,
    tumour_mask,
    alpha=0.5,
    label_info=label_color_dict,
    return_ax=True,
)
plt.savefig("tumour_overlay.png")
