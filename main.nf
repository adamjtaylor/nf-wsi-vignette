#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { IMAGE_ANALYSIS } from './workflows/image_analysis'

params.samplesheet = 'test_data/samplesheet.csv'
params.outdir = 'results'

workflow {
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
    IMAGE_ANALYSIS(image_ch)
}