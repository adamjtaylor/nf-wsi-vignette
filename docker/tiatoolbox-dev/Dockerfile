FROM ubuntu:24.04 AS builder-image

# Avoid tzdata blocking the build
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.12 and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    build-essential \
    git \
    libgl1 \
    libopenjp2-7-dev \
    libopenjp2-tools \
    openslide-tools \
    python3.12 \
    python3.12-venv \
    python3.12-dev &&\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add env to PATH
RUN python3.12 -m venv /venv
ENV PATH=/venv/bin:$PATH

# Install pip & dependencies
RUN pip install --upgrade pip setuptools wheel

# Clone TIAToolbox from GitHub (dev branch)
WORKDIR /workspace
RUN git clone --branch develop https://github.com/TissueImageAnalytics/tiatoolbox.git

# Install TIAToolbox dependencies
WORKDIR /workspace/tiatoolbox
RUN pip install -r requirements/requirements_dev.txt
RUN pip install huggingface-hub igraph leidenalg

# Install TIAToolbox in editable mode
RUN pip install -e .

# Set the working directory
WORKDIR /workspace

# Default command (change as needed)
CMD ["/bin/bash"]