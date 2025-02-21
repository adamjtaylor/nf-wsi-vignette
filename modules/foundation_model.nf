process FOUNDATION_MODEL {
    publishDir "${params.outdir}/foundation_model", mode: 'copy'

    input:
    tuple val(meta), path(image)

    output:
    tuple val(meta), path("${meta.id}_wsi_features"), emit: wsi_features

    script:
    """
    foundation_model.py --input ${image} --output ${meta.id}_wsi_features
    """
}