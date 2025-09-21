FROM python:3.10-slim

# Install system dependencies (excluding git since it will be installed by feature)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Copy UV directly from its official image and make it executable
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Set working directory
WORKDIR /workspaces/tidyworld

# Copy dependency files and README
COPY pyproject.toml README.md ./

# Install dependencies as root (they'll be accessible to vscode user)
RUN uv pip install --system pip setuptools wheel && \
    uv sync --no-dev

# Set the default shell to bash
ENV SHELL="/bin/bash"