FROM ghcr.io/divideprojects/docker-python-base:latest AS build
WORKDIR /app
COPY . .
RUN curl "https://arc.io/arc-sw.js" -o /app/WebStreamer/html/assets/static/arc-sw.js
RUN /venv/bin/poetry export -f requirements.txt --without-hashes --output requirements.txt
RUN pip install --disable-pip-version-check -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["-m", "WebStreamer"]
