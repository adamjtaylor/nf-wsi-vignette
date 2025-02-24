process FOUNDATION_MODEL {

    //container 'ghcr.io/tissueimageanalytics/tiatoolbox:1.6.0-py3.11-debian'
    container 'tiatoolbox-local-arm64'
    containerOptions '-v ~/.cache/huggingface:/root/.cache/huggingface'
    conda "/Users/ataylor/mambaforge/envs/tiatoolbox"


    publishDir "results/${meta.id}/foundation_model", mode: 'copy'

    input:
    tuple val(meta), path(image)

    output:
    tuple val(meta), path(image), path("wsi_features/0.features.0.npy"), path("wsi_features/0.position.npy"), path("wsi_features/file_map.dat"), emit: wsi_features

    script:
    """
    foundation_model.py ${image} ${projectDir}/models
    """
}

process FEATURE_REDUCTION {

    //container 'ghcr.io/tissueimageanalytics/tiatoolbox:1.6.0-py3.11-debian'
    container 'tiatoolbox-local-arm64'

    publishDir "results/${meta.id}/feature_reduction", mode: 'copy'

    input:
    tuple val(meta), path(image), path(features), path(positions), path(file_map)

    output:
    path '*.png'
    tuple val(meta), path('umap.npy'), path('knn_graph.npy'), emit: umap

    script:
    """
    feature_reduction.py ${image} ${features} ${positions}
    """
}
workflow  {
    samplesheet_ch = Channel.fromPath(params.samplesheet)
            // Split samplesheet and create channel
    image_ch = samplesheet_ch
        .splitCsv(header:true)
        .map {
            row ->
            def meta = [:]
            meta.id = file(row.image).simpleName
            meta.basename = file(row.image).baseName
            image = file(row.image)
            [meta, image]                
            }
    FOUNDATION_MODEL(image_ch)
    FEATURE_REDUCTION(FOUNDATION_MODEL.out.wsi_features)
}