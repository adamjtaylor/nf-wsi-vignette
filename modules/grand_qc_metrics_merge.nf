process MERGE_JSON_RESULTS {


    publishDir "results", mode: 'copy'
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
}