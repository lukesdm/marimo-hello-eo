import marimo

__generated_with = "0.9.14"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo

    from datetime import date

    import geopandas as gpd
    import planetary_computer
    import plotly.express as px
    import pystac_client
    import shapely
    import stackstac
    return (
        date,
        gpd,
        mo,
        planetary_computer,
        px,
        pystac_client,
        shapely,
        stackstac,
    )


@app.cell
def __(planetary_computer, pystac_client):
    # Perform Planetary Computer STAC search
    # https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    time_range = "2020-12-01/2020-12-31"
    bbox = [-122.2751, 47.5469, -121.9613, 47.7458]

    search = catalog.search(collections=["landsat-c2-l2"], bbox=bbox, datetime=time_range)
    items = search.item_collection()
    print(f"Found {len(items)} items.")
    return bbox, catalog, items, search, time_range


@app.cell
def __(items, stackstac):
    ds = stackstac.stack(items)
    # Drop metadata
    ds = ds.drop_vars([v for v in ds.coords if v not in ds.dims])
    # ds
    return (ds,)


@app.cell
def __(ds):
    x_offset = 3000
    y_offset = 3000
    size = 256
    ds_subset = ds.isel(x=range(x_offset,x_offset + size), y=range(y_offset,y_offset + size)).compute().rename("value")
    return ds_subset, size, x_offset, y_offset


@app.cell
def __(ds_subset, mo):
    # UI elements
    band = mo.ui.dropdown(ds_subset["band"].values, value="red", label="Band")
    timestep = mo.ui.slider(0, ds_subset.sizes["time"]-1, label="Date")
    return band, timestep


@app.cell
def __(ds_subset, timestep):
    # Date string for the given index
    timestep_label = str(ds_subset["time"].values[timestep.value])
    return (timestep_label,)


@app.cell
def __(band, ds_subset, mo, px, timestep, timestep_label):
    # Slice and plot image
    _ds_single = ds_subset.sel(band=band.value)[timestep.value]
    _plot = px.imshow(_ds_single, title=timestep_label)
    img_plot = mo.ui.plotly(_plot)
    return (img_plot,)


@app.cell
def __(band, ds_subset, img_plot, mo, px):
    # Plot selected pixels' mean time-series
    _plot = px.line(markers=True)
    _plot.update_layout(xaxis_title="Date", yaxis_title="Mean", title=f"Selected pixels: Mean {band.value} over time")

    if len(img_plot.ranges) > 0:
        _minx, _maxx = img_plot.ranges["x"][0], img_plot.ranges["x"][1]
        _miny, _maxy = img_plot.ranges["y"][1], img_plot.ranges["y"][0]

        _ds_sliced = ds_subset.sel(
                band=band.value,
                x=slice(_minx, _maxx),
                y=slice(_miny, _maxy),
                )
        
        _mean = _ds_sliced.mean(["x", "y"]).dropna(dim="time")
        _plot.data[0].x = _mean["time"]
        _plot.data[0].y = _mean

    mean_plot = mo.ui.plotly(_plot)
    return (mean_plot,)


@app.cell
def __(band, img_plot, mean_plot, mo, timestep):
    mo.vstack([band, timestep, img_plot, mean_plot])
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
