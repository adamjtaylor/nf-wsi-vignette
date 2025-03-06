process GRAND_QC_RUN {

    container 'ghcr.io/adamjtaylor/nf-wsi-vignette/grandqc:latest'
    conda "/Users/ataylor/mambaforge/envs/grandqc"
    label 'GPU'

    publishDir "${params.outdir}/${meta.id}/grand_qc/", mode: 'copy'

    input:
    tuple val(meta), path(image)
    each path(td_model)
    each path(qc_model)

    output:
    tuple val(meta), 
    path("output_images/maps_qc/*"), 
    path("output_images/mask_qc/*"), 
    path("output_images/overlays_qc/*"), 
    // Not outputting the tissue mask for now as it has a clash with the QC mask
    // as Nextflow has case-insensitive file paths and it has the same name
    //path("output_images/tis_det_mask/*"), 
    path("output_images/tis_det_mask_col/*"), 
    path("output_images/tis_det_overlay/*"), 
    path("output_images/tis_det_thumbnail/*"), 
    path("output_images/*stats_per_slide.txt"), 
    emit: grand_qc_output

    script:
    """
    mkdir input_images
    # Copy the input image to the temporary directory
    cp ${image} input_images/
    
    mkdir -p td_model qc_model
    cp ${td_model} td_model/
    cp ${qc_model} qc_model/

    # Run tissue detection first
    python ${projectDir}/grandqc/01_WSI_inference_OPENSLIDE_QC/wsi_tis_detect.py \
        --slide_folder ./input_images \
        --output_dir output_images \
        --model_dir td_model/

    echo "Tissue detection complete"

    # Run QC model
    python ${projectDir}/grandqc/01_WSI_inference_OPENSLIDE_QC/main.py \
        --slide_folder ./input_images \
        --output_dir output_images \
        --model_dir qc_model/

    echo "QC model complete"
    """

    stub:
    """
    mkdir -p output_images
    cd output_images
    mkdir -p maps_qc mask_qc overlays_qc tis_det_mask tis_det_mask_col tis_det_overlay tis_det_thumbnail
    touch maps_qc/${meta.id}_map_QC.png
    touch mask_qc/${meta.id}_mask.png
    touch overlays_qc/${meta.id}_overlay_QC.jpg
    touch tis_det_mask/${meta.id}_MASK.png
    touch tis_det_mask_col/${meta.id}_MASK_COL.png
    touch tis_det_overlay/${meta.id}_OVERLAY.jpg
    touch tis_det_thumbnail/${meta.id}.jpg
    touch stats_per_slide.txt
    """
}