FROM ghcr.io/prefix-dev/pixi:0.63.2-noble
WORKDIR /app

# Prevent environment (dependencies) folder being created in app folder, which kills perf on WSL.
RUN pixi config set --global detached-environments true

# Install dependencies
COPY app/pyproject.toml app/pixi.lock ./
RUN pixi install

# No need to copy anything else - it will be volume mounted.
# COPY . .

ENV MARIMO_SKIP_UPDATE_CHECK=1
EXPOSE 8080
CMD ["pixi", "run", "marimo", "edit", "--host", "0.0.0.0", "--port", "8080", "--no-token"]
