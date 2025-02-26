process EMBEDDING {

    //container 'ghcr.io/tissueimageanalytics/tiatoolbox:1.6.0-py3.11-debian'
    container 'tiatoolbox-local-arm64'
    containerOptions '-v ~/.cache/huggingface:/root/.cache/huggingface'
    conda "/Users/ataylor/mambaforge/envs/tiatoolbox"
    secret 'HF_TOKEN'
    publishDir "results/${meta.id}/foundation_model", mode: 'copy', pattern: "*.{npy,dat}"
    memory 24.GB

    input:
    tuple val(meta), path(image)

    output:
    tuple val(meta), path(image), path("wsi_features/0.features.0.npy"), path("wsi_features/0.position.npy"), path("wsi_features/file_map.dat"), emit: wsi_features

    script:
    """
    foundation_model.py ${image} $params.huggingface_hub_path $params.model
    """

    stub:
    """
    mkdir -p wsi_features
    touch "wsi_features/0.features.0.npy" 
    touch "wsi_features/0.position.npy"
    touch "wsi_features/file_map.dat"
    """
}
