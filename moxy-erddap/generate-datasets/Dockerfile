FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y curl jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY generate-datasets.sh ./

ENTRYPOINT ["/bin/bash", "/app/generate-datasets.sh"]
