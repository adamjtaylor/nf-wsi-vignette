include { GRAND_QC } from '../modules/grand_qc'
include { GRAND_QC_METRICS } from '../modules/grand_qc_metrics'
include { MERGE_JSON_RESULTS } from '../modules/grand_qc_metrics_merge'
include { GRAND_QC_REPORT } from '../modules/grand_qc_report'
include { FOUNDATION_MODEL } from '../modules/foundation_model'
include { EMBEDDING } from '../modules/embedding'
include { PATCH_SELECTION } from '../modules/patch_selection'
include { REPORT } from '../modules/report'

workflow IMAGE_ANALYSIS {
    take:
    samplesheet_ch

    main:
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
    // Run GRAND_QC
    GRAND_QC(image_ch)

    GRAND_QC_METRICS(GRAND_QC.out.grand_qc_output)

    // Join the QC metrics onto the GRAND_QC output by meta.id
    GRAND_QC.out.grand_qc_output.join(GRAND_QC_METRICS.out.qc_metrics, by: [0]).set { COMBINED }

    // Merge the QC metrics
    MERGE_JSON_RESULTS(GRAND_QC_METRICS.out.qc_metrics.map { it[1] }.collect())

    // Run the GRAND_QC_REPORT
    GRAND_QC_REPORT(COMBINED)
}