FROM mambaorg/micromamba:1.5.10-noble
COPY --chown=$MAMBA_USER:$MAMBA_USER conda/grand_qc.yml /tmp/conda.yml
RUN micromamba install -y -n base -f /tmp/conda.yml \
    && micromamba install -y -n base conda-forge::procps-ng \
    && micromamba env export --name base --explicit > environment.lock \
    && echo ">> CONDA_LOCK_START" \
    && cat environment.lock \
    && echo "<< CONDA_LOCK_END" \
    && micromamba clean -a -y
USER root
RUN apt-get update && apt-get install --yes git \
    && git clone --branch nextflow-compatible https://github.com/adamjtaylor/grandqc.git
ENV PATH="$MAMBA_ROOT_PREFIX/bin:$PATH"