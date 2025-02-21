#!/usr/bin/env python
import sys
import os
import json
import numpy as np
import cv2


def load_image(image_path):
    """Load an 8-bit grayscale PNG image."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return image


def analyze_qc_mask(image, id):
    """Calculate the pixel count and fraction of each artifact relative to total tissue pixels."""

    # for each region, calculate the number of pixels
    total_pixels = image.size
    total_tissue_pixels = np.sum((image != 0) & (image != 7))

    frac_tissue = total_tissue_pixels / total_pixels
    frac_background = np.sum(image == 7) / total_pixels
    frac_usable_tissue = np.sum(image == 1) / total_tissue_pixels
    frac_tissue_folds = np.sum(image == 2) / total_tissue_pixels
    frac_dark_spots_foreign_objects = np.sum(image == 3) / total_tissue_pixels
    frac_pen_markings = np.sum(image == 4) / total_tissue_pixels
    frac_air_bubbles_slide_edge = np.sum(image == 5) / total_tissue_pixels
    frac_out_of_focus = np.sum(image == 6) / total_tissue_pixels

    # Count the number of pixels with each integer value

    metrics = {
        "id": id,
        "total_pixels": total_pixels,
        "total_tissue_pixels": total_tissue_pixels,
        "frac_tissue": frac_tissue,
        "frac_background": frac_background,
        "frac_usable_tissue": frac_usable_tissue,
        "frac_tissue_folds": frac_tissue_folds,
        "frac_dark_spots_foreign_objects": frac_dark_spots_foreign_objects,
        "frac_pen_markings": frac_pen_markings,
        "frac_air_bubbles_slide_edge": frac_air_bubbles_slide_edge,
        "frac_out_of_focus": frac_out_of_focus,
    }
    return metrics


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python qc_mask_metrics.py <path_to_mask_image>" "<id>")
        sys.exit(1)

    mask_path = sys.argv[1]
    image = load_image(mask_path)
    metrics = analyze_qc_mask(image, sys.argv[2])
print(
    json.dumps(
        metrics,
        indent=2,
        default=lambda x: (
            int(x)
            if isinstance(x, np.integer)
            else float(x) if isinstance(x, np.floating) else x
        ),
    )
)
