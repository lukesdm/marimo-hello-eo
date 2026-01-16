ARG gdal_version=3.12.1
ARG marimo_version=0.19.4
ARG python_version=3.14

FROM ghcr.io/osgeo/gdal:ubuntu-small-${gdal_version}

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
ARG python_version
ENV VIRTUAL_ENV=/opt/venv
RUN mkdir -p ${VIRTUAL_ENV} && chown appuser:appuser ${VIRTUAL_ENV}
RUN uv venv ${VIRTUAL_ENV} --python ${python_version}

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

ARG gdal_version
RUN uv pip install gdal==${gdal_version}

# Install other Python libraries
RUN uv pip install rioxarray geopandas shapely planetary-computer stackstac dask[complete] plotly holoviews hvplot

# By default, the container runs as root so OS packages can be installed when the container is running.
# If running potentially untrusted code, uncomment the below.
# USER appuser

CMD . ${VIRTUAL_ENV}/bin/activate && marimo edit --no-token -p $PORT --host $HOST
