FROM ghcr.io/marimo-team/marimo:0.15.5

# Install OS packages, inc. GDAL.
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    libgdal-dev \
    python3-dev

# Install UV and make a virtual env.
COPY --from=ghcr.io/astral-sh/uv:0.8.6 /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1
RUN uv venv

#  GDAL Python bindings (which have to match version)
ENV GDAL_CONFIG=/usr/bin/gdal-config
RUN uv pip install gdal==3.6.2

# Install other Python libraries
RUN uv pip install rioxarray geopandas shapely planetary-computer stackstac dask[complete] plotly holoviews hvplot
