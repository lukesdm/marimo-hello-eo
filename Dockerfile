# Adapted from https://github.com/marimo-team/marimo/blob/main/docker/Dockerfile
# License: Apache License version 2.0 (http://www.apache.org/licenses/)
# Copyright 2025 Marimo Inc. (original) & Luke McQuade (modifications)

FROM python:3.13-slim

# Install OS packages, inc. GDAL.
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    libgdal-dev \
    python3-dev

# Make `uv` and `uvx` available in the PATH for all target images
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create a non-root user
RUN useradd -m appuser

WORKDIR /app

ARG marimo_version=0.16.2
ENV MARIMO_SKIP_UPDATE_CHECK=1
ENV UV_SYSTEM_PYTHON=1
RUN uv pip install --no-cache-dir marimo==${marimo_version} && \
  mkdir -p /app/data && \
  chown -R appuser:appuser /app

ENV PORT=8080
EXPOSE $PORT

ENV HOST=0.0.0.0

#  Install GDAL Python bindings
ENV GDAL_CONFIG=/usr/bin/gdal-config
RUN export GDAL_VERSION=$(gdal-config --version) && \
  uv pip install gdal==$GDAL_VERSION

# Install marimo & data deps
RUN uv pip install --no-cache-dir marimo[recommended,lsp] altair pandas numpy

# Install other Python libraries
RUN uv pip install rioxarray geopandas shapely planetary-computer stackstac dask[complete] plotly holoviews hvplot

CMD marimo edit --no-token -p $PORT --host $HOST
