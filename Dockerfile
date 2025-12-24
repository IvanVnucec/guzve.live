FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY . /app

ENV UV_NO_DEV=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

RUN uv sync --locked

CMD ["uv", "run", "main.py"]
