process FOUNDATION_MODEL {

    container 'ghcr.io/tissueimageanalytics/tiatoolbox:1.6.0-py3.11-debian'

    publishDir "${params.outdir}/foundation_model", mode: 'copy'

    input:
    tuple val(meta), path(image)

    output:
    tuple val(meta), path(image), path("${meta.id}_wsi_features"), emit: wsi_features

    script:
    """
    echo "Hello from the foundation model process"
    """
}