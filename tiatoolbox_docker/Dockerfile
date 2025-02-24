FROM --platform=linux/arm64 python:3.12-slim-bullseye

#get linux packages
RUN apt-get -y update && apt-get -y install --no-install-recommends \
    libopenjp2-7-dev libopenjp2-tools \
    openslide-tools \
    libgl1 \
    build-essential \
    && pip3 --no-cache-dir install tiatoolbox huggingface_hub \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir igraph leidenalg

