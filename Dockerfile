FROM ghcr.io/marimo-team/marimo:0.9.14

# Install GDAL and its Python bindings (which have to match version)
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    libgdal-dev \
    python3-dev
ENV GDAL_CONFIG=/usr/bin/gdal-config
RUN pip install gdal==3.6.2

# Install other Python libraries
RUN pip install rioxarray geopandas shapely planetary-computer stackstac dask[complete] plotly
