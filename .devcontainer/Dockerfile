FROM python:3.10-slim

# Install system dependencies (excluding git since it will be installed by feature)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry globally
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -

# Add Poetry to PATH for all users
ENV PATH="/opt/poetry/bin:$PATH"

# Configure Poetry globally
RUN /opt/poetry/bin/poetry config virtualenvs.in-project false

# Set working directory
WORKDIR /workspaces/tidyworld

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies as root (they'll be accessible to vscode user)
RUN /opt/poetry/bin/poetry install --no-root

# Set the default shell to bash
ENV SHELL /bin/bash
