process GRAND_QC_METRICS {

    container 'ghcr.io/adamjtaylor/nf-wsi-vignette/grandqc:latest'
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

process GRAND_QC_METRICS_MERGE {


    publishDir "${params.outdir}", mode: 'copy'
    container 'ubuntu:jammy'

    input:
    path results, stageAs: "?/*.json"

    output:
    path 'merged_results.json'

    script:
    """
    echo '[' > merged_results.json
    first=true
    for json in \$(ls -1 ${results} | sort); do
        if [ "\$first" = true ]; then
            first=false
        else
            echo ',' >> merged_results.json
        fi
        cat \$json >> merged_results.json
    done
    echo ']' >> merged_results.json
    """

    stub:
    """
    touch merged_results.json
    """
}