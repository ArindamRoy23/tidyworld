FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*.deb \
    && apt-get clean \
    && apt-get update
    
# System dependencies for Python builds, Docling, and dev tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    sudo \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

WORKDIR /workspaces/tidyworld

# Pre-install dependencies for faster container startup
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --group dev --no-install-project

ENV SHELL="/bin/bash"
ENV VIRTUAL_ENV="/workspaces/tidyworld/.venv"
ENV PATH="/workspaces/tidyworld/.venv/bin:${PATH}"
