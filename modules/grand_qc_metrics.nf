process GRAND_QC_METRICS {

    conda "/Users/ataylor/mambaforge/envs/grandqc"

    input:
    tuple val(meta), 
    path(map_qc), 
    path(mask_qc), 
    path(overlay_qc), 
    // path(tis_det_mask), 
    path(tis_det_mask_col), 
    path(tis_det_overlay), 
    path(tis_det_thumbnail), 
    path(stats_per_slide)

    output:
    tuple val(meta), path("qc_mask_percentages.json"), emit: qc_metrics

    script:
    """
    qc_mask_metrics.py ${mask_qc} ${meta.id} > qc_mask_percentages.json
    """

    stub:
    """
    touch qc_mask_percentages.json
    """

}