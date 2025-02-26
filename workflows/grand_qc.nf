include { GRAND_QC_RUN } from '../modules/grand_qc_run'
include { GRAND_QC_METRICS } from '../modules/grand_qc_metrics'
include { GRAND_QC_METRICS_MERGE } from '../modules/grand_qc_metrics'
include { GRAND_QC_REPORT } from '../modules/grand_qc_report'

workflow GRAND_QC {
    take:
    image_ch

    main:

    // Run GRAND_QC
    GRAND_QC_RUN(image_ch)

    GRAND_QC_METRICS(GRAND_QC_RUN.out.grand_qc_output)

    // Join the QC metrics onto the GRAND_QC output by meta.id
    GRAND_QC_RUN.out.grand_qc_output.join(GRAND_QC_METRICS.out.qc_metrics, by: [0]).set { COMBINED }

    // Merge the QC metrics
    GRAND_QC_METRICS_MERGE(GRAND_QC_METRICS.out.qc_metrics.map { it[1] }.collect())

    // Run the GRAND_QC_REPORT
    GRAND_QC_REPORT(COMBINED)

}