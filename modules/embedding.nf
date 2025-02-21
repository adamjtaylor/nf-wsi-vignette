process EMBEDDING {
    publishDir "${params.outdir}/embedding", mode: 'copy'

    input:
    tuple val(meta), path(image), path(wsi_features)

    output:
    tuple val(meta), path("${meta.id}_cluster_overlay.png"), emit: cluster_overlay
    tuple val(meta), path("${meta.id}_embeddings.npy"), emit: embeddings

    script:
    """
    embedding.py --input ${image} --features ${wsi_features} --output-prefix ${meta.id}
    """

    stub:
    """
    touch ${meta.id}_cluster_overlay.png
    touch ${meta.id}_embeddings.npy
    """
}