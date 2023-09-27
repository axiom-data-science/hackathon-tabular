#!/bin/bash

RESULTS_DIR=./responses
rm -rf "$RESULTS_DIR"
mkdir -p "$RESULTS_DIR"

docker compose logs nginx | grep 'GET /erddap' | awk '{print $9}' | sort | uniq | while read -r req; do
  echo $req
  docker compose exec --no-TTY --interactive=false erddap curl -sSL "http://localhost:8080${req}" > "${RESULTS_DIR}/${req//\//@}"
done
