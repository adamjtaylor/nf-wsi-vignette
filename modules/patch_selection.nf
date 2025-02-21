process PATCH_SELECTION {
    publishDir "${params.outdir}/patch_selection", mode: 'copy'

    input:
    tuple val(meta), path(image), path(wsi_features), path(embeddings)

    output:
    tuple val(meta), path("${meta.id}_representative_patches"), emit: representative_patches

    script:
    """
    patch_selection.py --input ${image} --features ${wsi_features} --embeddings ${embeddings} --output ${meta.id}_representative_patches
    """
}