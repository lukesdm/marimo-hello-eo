# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "planetary-computer",
#     "plotly",
#     "stackstac",
#     "shapely",
# ]
# ///

import marimo

__generated_with = "0.15.5"
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

    A quick demonstration of using Earth observation (EO) data in a [marimo](https://marimo.io/) notebook. Based on tutorials from [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/).

    If the notebook doesn't run automatically, click ▶️ in the bottom right of the screen to get started.

    Author: Luke McQuade @ [EO Analytics](https://www.plus.ac.at/geoinformatik/research/research-areas/eo-analytics/?lang=en), Z_GIS, Paris Lodron Universität Salzburg.

    GitHub reposistory: https://github.com/lukesdm/marimo-hello-eo.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Perform Planetary Computer STAC search

    Search the STAC API for Landsat 8/9 images from [Landast Collection 2](https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2).

    See also https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/
    """
    )
    return


@app.cell
def _(planetary_computer, pystac_client, shapely):
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    # ⚙️ Once familiar with the notebook, try changing this!
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

    # Select only Landsat 8 and 9.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Load the data

    For convenience, downsample to 200m and preload it into memory.
    """
    )
    return


@app.cell
def _(bbox, items, stackstac):
    # Also for convenience, reproject to EPSG3857.
    ds = stackstac.stack(
        items, epsg=3857, bounds_latlon=bbox, resolution=200
    ).compute().rename("value")

    # Drop metadata for convenience when plotting
    ds = ds.drop_vars([v for v in ds.coords if v not in ds.dims])
    return (ds,)


@app.cell(hide_code=True)
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
    # Slice data and create image plot
    _ds_single = ds.sel(band=band.value)[timestep.value]
    _plot = px.imshow(
        _ds_single, title=timestep_label, width=525, height=500,
        # Flip Y axis
        origin="lower"
    )
    # Reduce space between title and plot
    _plot.update_layout(margin={"t": 50})

    img_plot = mo.ui.plotly(_plot)
    return (img_plot,)


@app.cell
def _(band, ds, img_plot, mo, px):
    # Create a plot of the selected pixels' mean time-series
    _plot = px.line(markers=True, height=500, width=500)
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
    # Display the UI elements and plots
    mo.vstack(
        [
            mo.hstack([band, timestep], justify="start"),
            mo.hstack([img_plot, mean_plot]),
        ]
    )
    return


@app.cell(hide_code=True)
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
