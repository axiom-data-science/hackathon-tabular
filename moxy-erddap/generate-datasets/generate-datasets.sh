#!/bin/bash

MOXY_URL="http://localhost:8000"
OUTPUT_DIR="./datasets.d/moxy"

while getopts ":m:o:" opt; do
  case ${opt} in
    m )
      MOXY_URL=$OPTARG
      ;;
    o )
      OUTPUT_DIR=$OPTARG
      ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      ;;
  esac
done
shift $((OPTIND -1))

mkdir -p "${OUTPUT_DIR}"

curl -sSL "${MOXY_URL}/datasets" | jq -r '.[]' | while read -r dataset; do
  cat > "${OUTPUT_DIR}/${dataset}.xml" <<EOF
<dataset type="EDDTableFromErddap" datasetID="${dataset}">
  <sourceUrl>${MOXY_URL}/erddap/tabledap/${dataset}</sourceUrl>
  <reloadEveryNMinutes>10</reloadEveryNMinutes>
  <subscribeToRemoteErddapDataset>false</subscribeToRemoteErddapDataset>
  <redirect>false</redirect>
</dataset>
EOF
done
