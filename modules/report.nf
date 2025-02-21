process REPORT {
    publishDir "${params.outdir}/report", mode: 'copy'

    input:
    tuple val(meta), path(artefact_mask), path(artefact_overlay), path(tissue_mask), path(tissue_overlay), path(thumbnail)
    tuple val(meta2), path(cluster_overlay)
    tuple val(meta3), path(representative_patches)

    output:
    path "${meta.id}_report.md", emit: report

    script:
    """
    generate_report.py --meta ${meta.id} \
                       --artefact-mask ${artefact_mask} \
                       --artefact-overlay ${artefact_overlay} \
                       --tissue-mask ${tissue_mask} \
                       --tissue-overlay ${tissue_overlay} \
                       --thumbnail ${thumbnail} \
                       --cluster-overlay ${cluster_overlay} \
                       --representative-patches ${representative_patches} \
                       --output ${meta.id}_report.md
    """
}