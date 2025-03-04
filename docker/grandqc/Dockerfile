# Stage 1: Build Environment using Miniconda
FROM continuumio/miniconda3 AS build

# Maintainer information
LABEL maintainer="Adam Taylor <adam.taylor@sagebase.org>"

# Copy Conda environment file
COPY conda/grand_qc.yml environment.yml

# Create and pack the Conda environment
RUN conda env create -f environment.yml && \
    conda install -c conda-forge conda-pack && \
    conda-pack -n grandqc -o /tmp/env.tar && \
    mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar

# Fix paths after unpacking Conda
RUN /venv/bin/conda-unpack

# Stage 2: Runtime Environment
FROM debian:bullseye AS runtime

# Copy Conda environment from the build stage
COPY --from=build /venv /venv

# Set up shell and install system dependencies
SHELL ["/bin/bash", "-c"]
RUN apt-get update && apt-get install --yes --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone GrandQC repo
RUN source /venv/bin/activate && \
    git clone --branch nextflow-compatible https://github.com/adamjtaylor/grandqc.git

# Set environment variables
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Default command
CMD ["/bin/bash"]