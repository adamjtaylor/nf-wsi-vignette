FROM ubuntu:22.04 AS builder-image

# Avoid tzdata blocking the build
ENV DEBIAN_FRONTEND=noninteractive

# Install python3.12
RUN apt-get update && \
    apt install software-properties-common -y &&\
    add-apt-repository ppa:deadsnakes/ppa -y && apt update &&\
    apt-get install -y --no-install-recommends python3.12-venv &&\
    apt-get install libpython3.12-de -y &&\
    apt-get install python3.12-dev -y &&\
    apt-get install build-essential -y &&\
    apt-get clean

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

# Install TIAToolbox in editable mode
RUN pip install -e .

# Set the working directory
WORKDIR /workspace

# Default command (change as needed)
CMD ["/bin/bash"]