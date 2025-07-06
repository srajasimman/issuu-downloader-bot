# Install uv
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the project into the image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Set the entrypoint to run the application
ENTRYPOINT ["uv", "run", "main.py", "bot"]

# Metadata for the Docker image
LABEL maintainer="S Rajasimman" \
        org.opencontainers.image.source="https://github.com/srajasimman/issuu-downloader-bot" \
        org.opencontainers.image.description="A Telegram bot to download Issuu documents as PDFs." \
        org.opencontainers.image.licenses="MIT" \
        org.opencontainers.image.version="1.0.0" \
        org.opencontainers.image.url="ghcr.io/srajasimman/issuu-downloader-bot" \
        org.opencontainers.image.documentation="README.md" \
        org.opencontainers.image.vendor="S Rajasimman" \
        org.opencontainers.image.title="Issuu Downloader Bot" \
        org.opencontainers.image.revision="latest"