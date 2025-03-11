

include { EMBEDDING } from '../modules/foundation_model_embedding'
include { CLUSTERING } from '../modules/foundation_model_clustering'
include { EMBEDDING_REPORT } from '../modules/foundation_model_report'
include { GATHER } from '../modules/foundation_model_embedding'

workflow TIA_TOOLBOX {
    
    take:
    image_ch

    main:

    EMBEDDING(image_ch)
    CLUSTERING(EMBEDDING.out.wsi_features)
    EMBEDDING_REPORT(CLUSTERING.out.plots)

    GATHER(EMBEDDING.out.wsi_features)
}