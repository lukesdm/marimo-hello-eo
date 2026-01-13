ARG GDAL_VERSION=3.12.1
ARG marimo_version=0.19.2

FROM ghcr.io/osgeo/gdal:ubuntu-small-${GDAL_VERSION}

# <MARIMO>
# Adapted from https://github.com/marimo-team/marimo/blob/main/docker/Dockerfile
# License: Apache License version 2.0 (http://www.apache.org/licenses/)
# Copyright 2025 Marimo Inc.
#------------------------------------------------------------------------------
# syntax=docker/dockerfile:1.12

# Make `uv` and `uvx` available in the PATH for all target images
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create a non-root user
RUN useradd -m appuser

WORKDIR /app

# Make venv - outside of app dir so it doesn't conflict with host mounted files.
ENV VIRTUAL_ENV=/opt/venv
RUN mkdir -p ${VIRTUAL_ENV} && chown appuser:appuser ${VIRTUAL_ENV}
RUN uv venv ${VIRTUAL_ENV} --python 3.14

ARG marimo_version
ENV MARIMO_SKIP_UPDATE_CHECK=1
RUN uv pip install --no-cache-dir marimo==${marimo_version} && \
  mkdir -p /app/data && \
  chown -R appuser:appuser /app

ENV PORT=8080
EXPOSE $PORT

ENV HOST=0.0.0.0

RUN uv pip install --no-cache-dir marimo[recommended,lsp] altair pandas numpy

# </MARIMO>
#------------------------------------------------------------------------------
#
# Ours...

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev

ARG GDAL_VERSION
RUN uv pip install gdal==${GDAL_VERSION}

# Install other Python libraries
RUN uv pip install rioxarray geopandas shapely planetary-computer stackstac dask[complete] plotly holoviews hvplot

# USER appuser

CMD . ${VIRTUAL_ENV}/bin/activate && marimo edit --no-token -p $PORT --host $HOST
