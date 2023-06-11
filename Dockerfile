FROM ghcr.io/divkix/docker-python-base:latest
WORKDIR /app
COPY . .
RUN poetry install --only main --no-interaction --no-ansi \
    && rm -rf /root/.cache/pip /root/.cache/pypoetry
CMD ["poetry", "run", "python3", "-m", "WebStreamer"]

HEALTHCHECK --interval=60s --timeout=30s --start-period=180s --retries=5 CMD curl --fail http://localhost:$PORT || exit 1

LABEL org.opencontainers.image.authors="Divanshu Chauhan <divkix@divkix.me>"
LABEL org.opencontainers.image.url="https://divkix.me"
LABEL org.opencontainers.image.source="https://github.com/divkix/FileStreamerBot"
LABEL org.opencontainers.image.title="FileStreamerBot"
LABEL org.opencontainers.image.description="Official FileStreamerBot Docker Image"
LABEL org.opencontainers.image.vendor="Divkix"
