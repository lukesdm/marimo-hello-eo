import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from datetime import date

    import planetary_computer
    import plotly.express as px
    import pystac_client
    import shapely
    import stackstac
    return mo, planetary_computer, px, pystac_client, shapely, stackstac


@app.cell
def _(mo):
    mo.md(
        r"""
    # Hello Landsat

    A quick demonstration of using Earth observation (EO) data in a [marimo](https://marimo.io/) notebook.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Perform Planetary Computer STAC search

    Search the [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/) STAC API for Landsat 8/9 images.

    See also https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/.
    """
    )
    return


@app.cell
def _(planetary_computer, pystac_client, shapely):
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    time_range = "2023-04-01/2023-04-30"

    # Area of interest (AoI) bounding box
    lat_min, lon_min = 27.706, -15.843
    lat_max, lon_max = 28.203, -15.321

    bbox = (lon_min, lat_min, lon_max, lat_max)
    _bbox = shapely.box(*bbox)
    _bbox_coords = list(_bbox.exterior.coords)

    # Select only images completely containing the AoI
    _cql2_contains = {
        "op": "s_contains",
        "args": [
            {"property": "geometry"},
            {"type": "Polygon", "coordinates": [_bbox_coords]},
        ],
    }

    # Select only Landsat 8 and 9 (not 7).
    _cql2_platform = {
        "op": "in",
        "args": [{"property": "platform"}, ["landsat-8", "landsat-9"]],
    }

    search = catalog.search(
        collections=["landsat-c2-l2"],
        bbox=bbox,
        datetime=time_range,
        filter={"op": "and", "args": [_cql2_contains, _cql2_platform]},
    )
    items = search.item_collection()
    print(f"Found {len(items)} items.")
    return bbox, items


@app.cell
def _(mo):
    mo.md(r"""## Load the data""")
    return


@app.cell
def _(bbox, items, stackstac):
    # For convenience, downsample to 200m and reproject to EPSG3857.
    ds = stackstac.stack(
        items, epsg=3857, bounds_latlon=bbox, resolution=200
    ).compute().rename("value")

    # Drop metadata for convenience when plotting
    ds = ds.drop_vars([v for v in ds.coords if v not in ds.dims])
    return (ds,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Construct a simple UI and display it

    The UI elements showcase marimo's reactivity—as one thing is changed, the other elements update automatically.
    """
    )
    return


@app.cell
def _(ds, mo):
    # UI elements
    band = mo.ui.dropdown(ds["band"].values, value="red", label="Band")
    timestep = mo.ui.slider(0, ds.sizes["time"]-1, label="Date")
    return band, timestep


@app.cell
def _(ds, timestep):
    # Date string for the given index
    timestep_label = str(ds["time"].values[timestep.value])
    return (timestep_label,)


@app.cell
def _(band, ds, mo, px, timestep, timestep_label):
    # Slice and plot image
    _ds_single = ds.sel(band=band.value)[timestep.value]
    _plot = px.imshow(_ds_single, title=timestep_label, width=550, height=550)
    img_plot = mo.ui.plotly(_plot)
    return (img_plot,)


@app.cell
def _(band, ds, img_plot, mo, px):
    # Plot selected pixels' mean time-series
    _plot = px.line(markers=True, height=500)
    _plot.update_layout(xaxis_title="Date", yaxis_title="Mean", title=f"Selected pixels: Mean {band.value} over time")

    if len(img_plot.ranges) > 0:
        _minx, _maxx = img_plot.ranges["x"][0], img_plot.ranges["x"][1]
        _miny, _maxy = img_plot.ranges["y"][1], img_plot.ranges["y"][0]

        _ds_sliced = ds.sel(
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
def _(band, img_plot, mean_plot, mo, timestep):
    mo.vstack([band, timestep, mo.hstack([img_plot, mean_plot])])
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ☝️ Try exploring the images, then select a region of pixels.

    (A known issue: when you change the image date/band, the chart resets.)
    """
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
