#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { IMAGE_ANALYSIS } from './workflows/image_analysis'

params.samplesheet = 'test_data/samplesheet.csv'
params.outdir = 'results'

workflow {
    samplesheet_ch = Channel.fromPath(params.samplesheet)
    IMAGE_ANALYSIS(samplesheet_ch)
}