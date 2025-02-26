process GRAND_QC_REPORT {
    publishDir "${params.outdir}/${meta.id}/report/", mode: 'copy'
    input:
    tuple val(meta), 
        path(qc_map), 
        path (qc_mask),
        path(qc_overlay), 
        path(tissue_mask_colored), 
        path(tissue_overlay), 
        path(thumbnail), 
        path(stats), 
        path(metrics)

    output:
    path 'qc_report.md'
    path 'images/*.{png,jpg}'

    script:
"""
# Ensure the input paths end up in the publishDir
mkdir -p images
cp ${qc_map} ${qc_overlay} ${tissue_mask_colored} ${tissue_overlay} ${thumbnail} "images/"

# Generate a combined Markdown table with Stats & Metrics
(
echo "| Metric | Value |"
echo "|--------|-------|"

# Convert the stats file into table rows
awk 'BEGIN { FS = "\t" } 
NR > 1 {
    print "| **File Name** | " \$1 " |"
    print "| **Objective Power** | " \$2 "x |"
    print "| **Resolution (um/px)** | " \$3 " |"
    print "| **Height (px, mm)** | " \$7 " px,  " sprintf("%.3f", (\$7 * \$3)/1000) " mm |"
    print "| **Width** | " \$8 " px / " sprintf("%.3f", (\$8 * \$3)/1000) " mm |"
}' ${stats}

# Process the metrics JSON file and append to the table
jq -r '
def roundit: . * 100 | round / 100;

# Define human-readable key mappings
def keymap:
{
    "id": "Sample ID",
    "total_pixels": "Total Pixels",
    "total_tissue_pixels": "Total Tissue Pixels",
    "frac_tissue": "Tissue (% of image)",
    "frac_background": "Background (% of image)",
    "frac_usable_tissue": "Usable Tissue (% of tissue)",
    "frac_tissue_folds": "Tissue Folds (% of tissue)",
    "frac_dark_spots_foreign_objects": "Dark Spots & Foreign Objects (% of tissue)",
    "frac_pen_markings": "Pen Markings (% of tissue)",
    "frac_air_bubbles_slide_edge": "Air Bubbles / Slide Edge (% of tissue)",
    "frac_out_of_focus": "Out of Focus (% of tissue)"
};

# Convert JSON to entries, replace keys, and process values
to_entries | map(
    "| **\\(keymap[.key] // .key)** | \\(
        if (.key | startswith(\"frac\")) then 
            (.value * 100 | roundit) 
        elif (.value | type == \"number\") then 
            (.value | roundit) 
        else 
            .value 
        end
    ) |"
) | join("\n")
' ${metrics}
) > stats_and_metrics.md

# Create the final QC report
cat <<EOF > qc_report.md
# QC Report

This report presents metrics from the image analysis of sample ${meta.id}. Images were processed using GrandQC, 
a deep learning-based tool designed to assess whole-slide image integrity and detect common artifacts. 
By segmenting tissue and identifying issues such as folds, pen marks, and out-of-focus regions, GrandQC 
helps ensure that image data is well-characterized for downstream analysis.

## Thumbnail
<img src="images/\$(basename ${thumbnail})" width="400">

## Stats & Metrics
\$(cat stats_and_metrics.md)

## Tissue Mask

<div style="display: flex; gap: 10px; align-items: flex-start;">
    <figure>
        <img src="images/\$(basename ${tissue_mask_colored})" width="400" alt="Tissue Mask">
        <figcaption>Tissue Mask</figcaption>
    </figure>
    <figure>
        <img src="images/\$(basename ${tissue_overlay})" width="400" alt="Tissue Mask Overlay">
        <figcaption>Tissue Overlay</figcaption>
    </figure>
</div>

## Artefact Map
<div style="display: flex; gap: 20px; align-items: flex-start;">
    <figure>
        <img src="images/\$(basename ${qc_map})" width="400" alt="QC Map">
        <figcaption>QC Map</figcaption>
    </figure>
    <figure>
        <img src="images/\$(basename ${qc_overlay})" width="400" alt="QC Overlay">
        <figcaption>QC Overlay</figcaption>
    </figure>
</div>

<span style="color: #FFFFFF;">&#9632;</span> Background (White) | 
<span style="color: #808080;">&#9632;</span> Usable Tissue (Gray) |
<span style="color: #FF6347;">&#9632;</span> Tissue Folds (Orange) |
<span style="color: #00FF00;">&#9632;</span> Dark Spots & Foreign Objects (Lime) |
<span style="color: #FF0000;">&#9632;</span> Pen Markings (Red) |
<span style="color: #FF00FF;">&#9632;</span> Air Bubbles / Slide Edge (Magenta) |
<span style="color: #4B0082;">&#9632;</span> Out of Focus (Indigo)

## Methods  

Whole-slide images (WSIs) for sample **${meta.id}** were analyzed using GrandQC, an open-source deep learning-based tool for tissue segmentation and artifact detection. The analysis was performed in two stages:  

1. **Tissue Segmentation:** GrandQC’s tissue detection model identified tissue regions, distinguishing them from the background to provide a refined target for subsequent artifact detection.  
2. **Artifact Segmentation:** A pre-trained GrandQC artifact model was applied to detect and classify common slide artifacts, including tissue folds, pen markings, dark spots, air bubbles, slide edges, and out-of-focus regions.  

GrandQC models were selected based on the optimal balance of accuracy and efficiency, with analysis performed at 7x magnification. The outputs include segmented tissue masks and artifact maps, which provide insights into potential issues affecting image integrity.
EOF
"""

stub:
"""
touch qc_report.md
mkdir -p images
touch images/thumbnail.png
"""
}
