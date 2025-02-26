process PREDICT_TUMOR {

    //container 'ghcr.io/tissueimageanalytics/tiatoolbox:1.6.0-py3.11-debian'
    container 'tiatoolbox-local-arm64'
    conda "/Users/ataylor/mambaforge/envs/tiatoolbox"
    publishDir "results/${meta.id}/predict_tumor", mode: 'copy'

    input:
    tuple val(meta), path(image)

    output:
    tuple val(meta), path("tumour_mask.png"), path("tumour_overlay.png"), emit: tumor_predictions

    script:
    """
    predict_tumor.py ${image}
    """

}
