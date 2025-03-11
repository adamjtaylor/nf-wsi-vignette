process EMBEDDING {
    container 'ghcr.io/adamjtaylor/nf-wsi-vignette/tiatoolbox:latest'
    containerOptions '-v ~/.cache/huggingface:/root/.cache/huggingface'
    conda "/Users/ataylor/mambaforge/envs/tiatoolbox"
    label 'GPU'
    secret 'HF_TOKEN'

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

process GATHER {
    container 'community.wave.seqera.io/library/pip_pyarrow:1aa2dddb3572991c'
    conda "/Users/ataylor/mambaforge/envs/tiatoolbox"

    publishDir "results/${meta.id}/${params.model}", mode: 'copy', pattern: "features.parquet"

    input:
    tuple val(meta), path(image), path(features), path(positions), path(file_map)

    output:
    tuple val(meta), path("features.parquet"), emit: gathered_features

    script:
    """
    gather_features.py ${meta.id} ${features} ${positions}
    """


}