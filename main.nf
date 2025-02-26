#!/usr/bin/env nextflow

nextflow.enable.dsl = 2


params.samplesheet = 'test_data/samplesheet.csv'
params.outdir = 'results'
params.grand_qc = true
params.foundation = false
params.huggingface_hub_path = "/Users/ataylor/.cache/huggingface"
// Model can be one of UNI, Prov-GigaPath, H-optimus-0
params.model = "H-optimus-0"



include { GRAND_QC } from './workflows/grand_qc.nf'
include { TIA_TOOLBOX } from './workflows/tia_toolbox.nf'
include { GRAND_QC_RUN } from './modules/grand_qc_run.nf'


workflow {

    log.info """
---------------
NF-WSI-VIGNETTE
---------------
Adam J. Taylor
Sage Bionetworks
---------------
Generating QC reports and feature embeddings for whole slide images
-----------------------------------------------------------------
params:
    samplesheet          : ${params.samplesheet}
    outdir               : ${params.outdir}
    grandqc              : ${params.grand_qc}
    foundation           : ${params.foundation}
    foundation_model     : ${params.model}
    huggingface_hub_path : ${params.huggingface_hub_path}

profile: ${workflow.profile}
-----------------------------------------------------------------
"""

    // Check if model is valid
    if (params.model != "UNI" && params.model != "Prov-GigaPath" && params.model != "H-optimus-0") {
        log.error "Invalid model specified. Please choose from UNI, Prov-GigaPath, H-optimus-0"
        exit 1
    }

    // Split samplesheet and map to image
    samplesheet_ch = Channel.fromPath(params.samplesheet)
    image_ch = samplesheet_ch
        .splitCsv(header:true)
        .map {
                row ->
                def meta = [:]
                meta.id = file(row.image).simpleName
                meta.basename = file(row.image).baseName
                def image = file(row.image)
                [meta, image]                
            }

    // Run GrandQC
    if (params.grand_qc) {
        GRAND_QC(image_ch)
    }

    // Run TIA Toolbox
    if (params.foundation) {
        TIA_TOOLBOX(image_ch)
    }
    
}