process CLUSTERING {

    container 'ghcr.io/adamjtaylor/nf-wsi-vignette/tiatoolbox:latest'
    conda "/Users/ataylor/mambaforge/envs/tiatoolbox"

    publishDir "results/${meta.id}/${params.model}/feature_reduction", mode: 'copy'

    input:
    tuple val(meta), path(image), path(features), path(positions), path(file_map)

    output:
    tuple val(meta), path('umap.npy'), path('knn_graph.npy'), emit: umap
    tuple val(meta), 
        path('overview.png'), 
        path('umap_overlay_merged.png'), 
        path('cluster_overlay_merged.png'),
        path('selected_patches_overlay.png'), 
        path('extracted_patches.png'),
        emit: plots

    script:
    """
    feature_reduction.py ${image} ${features} ${positions} $params.model
    """

    stub:
    """
    touch umap.npy knn_graph.npy
    touch overview.png umap_overlay_merged.png cluster_overlay_merged.png selected_patches_overlay.png extracted_patches.png
    """
}