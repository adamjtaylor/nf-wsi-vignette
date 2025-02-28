process GRAND_QC_GET_MODELS {
    container 'ghcr.io/adamjtaylor/nf-wsi-vignette/grandqc:latest'
    
    output:
    tuple path("td"), path("qc"), emit: grand_qc_models

    script:
    """
    mkdir -p td qc
    wget -O td/ https://zenodo.org/records/14507273/files/Tissue_Detection_MPP10.pth
    wget -O qc/ https://zenodo.org/records/14041538/files/GrandQC_MPP15.pth
    """

    stub:
    """
    mkdir -p td qc
    touch td/Tissue_Detection_MPP10.pth
    touch qc/GrandQC_MPP15.pth
    """
}