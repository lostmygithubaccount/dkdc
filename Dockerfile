# Base image
FROM ghcr.io/astral-sh/uv:alpine

# Install dependencies
# TODO: swtich to uv for Python installation
# see https://docs.astral.sh/uv/guides/integration/docker/#installing-python-in-arm-musl-images
RUN apk add --no-cache \
    zola \
    python3=~3.12 \
    python3-dev=~3.12 \
    bash

# Force uv to use system Python and disable auto-downloads
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_PYTHON=/usr/bin/python3

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY .python-version .python-version
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
COPY README.md README.md

# Copy project directories
COPY bin/ bin/
COPY websites/ websites/
COPY src/ src/
COPY packages/ packages/
COPY apps/ apps/

# Install Python dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Default command
CMD ["/bin/bash"]

