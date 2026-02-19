A simple [marimo](https://github.com/marimo-team/marimo) notebook/app and container environment for getting started with Earth Observation-oriented work. The notebook can be found here: [app/hello-landsat.py](app/hello-landsat.py).

Get started with, e.g., `docker compose up --build`, and browse to `http://localhost:8080`.

Or, outside a container with [pixi](https://pixi.prefix.dev/latest/) ([installation](https://pixi.prefix.dev/latest/installation/)):

```
cd app
pixi install
pixi run marimo edit
```
