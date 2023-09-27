#!/bin/bash

echo "Requests (path only)"
docker compose logs nginx | grep 'GET /erddap' | awk '{print $9}' | cut -d\? -f1 | sort | uniq -c

echo
echo "Requsts (unique)"
docker compose logs nginx | grep 'GET /erddap' | awk '{print $9}' | sort | uniq -c

echo
echo "Requests (with query parameters)"
docker compose logs nginx | grep 'GET /erddap' | awk '{print $9}'
