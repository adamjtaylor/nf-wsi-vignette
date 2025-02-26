process EMBEDDING_REPORT {
    publishDir "${params.outdir}/${meta.id}/report/", mode: 'copy'
    input:
    tuple val(meta), 
        path(overview), 
        path(umap_overlay), 
        path(leiden_overlay),
        path(patches_overlay), 
        path(patches)
    output:
    path 'foundation_model_report.md'
    path 'images/*.{png,jpg}'

    script:
"""
# Ensure the input paths end up in the publishDir
mkdir -p images
cp ${overview} ${umap_overlay} ${leiden_overlay} ${patches_overlay} ${patches} "images/"


# Create the final QC report
cat <<EOF > foundation_model_report.md
# Foundation model Embedding

This report presents visualisations from from the embedding of sample ${meta.id} using the ${meta.model}, digital pathology foundatio model. The embedding was generated using the TIA Toolbox, an open-source tool for digital pathology analysis. The report includes an overview of the embedding, a UMAP overlay, a Leiden clustering overlay, and selected patches from the embedding.

## Overview
<figure>
    <img src="images/\$(basename ${overview})" width="800" alt="Overview of Embedding">
    <figcaption>WSI overview</figcaption>
</figure>

## Leiden Clustering
<figure>
    <img src="images/\$(basename ${leiden_overlay})" width="800" alt="Leiden Clustering of Embedding Vectors">
    <figcaption>Leiden clustering of embedding vectors</figcaption>
</figure>

## Selected Patches
Five representative patches of each cluster were selected by distance to the cluster centroid. The patches are shown below.

<figure>
    <img src="images/\$(basename ${patches_overlay})" width="800" alt="Selected patch locations">
    <figcaption>Selected patch locations</figcaption>
</figure>
<figure>
    <img src="images/\$(basename ${patches})" width="800" alt="Selected patches">
    <figcaption>Selected patches</figcaption>
</figure>


EOF
"""

stub:
"""
touch foundation_model_report.md
mkdir -p images
touch images/overview.png
"""
}
