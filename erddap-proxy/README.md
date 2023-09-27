# erddap-remote-fingerprint

Examine traffic between a proxying ERDDAP configured with a remote
dataset (`EDDTableFromERDDAP`) proxying another local ERDDAP, with
nginx in between to log requested URLs.

# Requirements

Reasonably up to date docker compose supporting the compose spec.

# Usage

Run the compose stack. Health checks which wait for ERDDAP datasets to
initialize are included in the compose file, so this can take a minute or two.

```
docker compose up -d
```

The stack will spin up (in order):

* A "remote" ERDDAP with a single dataset to be proxied (`cwwcNDBCMet`)
* An nginx server proxying the "remote" ERDDAP
* An ERDDAP configured with an `EDDTableFromERDDAP` dataset to proxy the "remote" ERDDAP
* A script to execute some example requests (html, csv, nc, etc) against the proxying ERDDAP

Once the stack `up` finishes, the following to view the proxy requests logged in nginx:

```
./show_requests.sh
```

## Example output

```
Requests (path only)
      3 /erddap/files/cwwcNDBCMet/.csv
      5 /erddap/tabledap/cwwcNDBCMet.nccsv
      2 /erddap/tabledap/cwwcNDBCMet.nccsvMetadata
      2 /erddap/version

Requests (with query parameters)
/erddap/version
/erddap/tabledap/cwwcNDBCMet.nccsvMetadata
/erddap/files/cwwcNDBCMet/.csv
/erddap/tabledap/cwwcNDBCMet.nccsv?station,longitude,latitude&distinct()
/erddap/tabledap/cwwcNDBCMet.nccsv?station%2Clongitude%2Clatitude%2Ctime%2Cwd%2Cwspd%2Cgst%2Cwvht%2Cdpd%2Capd%2Cmwd%2Cbar%2Catmp%2Cwtmp%2Cdewp%2Cvis%2Cptdy%2Ctide%2Cwspu%2Cwspv&time%3E=2023-09-20T00%3A00%3A00Z&time%3C=2023-09-27T14%3A52%3A00Z
/erddap/tabledap/cwwcNDBCMet.nccsv?station%2Clongitude%2Clatitude%2Ctime%2Cwd%2Cwspd%2Cgst%2Cwvht%2Cdpd%2Capd%2Cmwd%2Cbar%2Catmp%2Cwtmp%2Cdewp%2Cvis%2Cptdy%2Ctide%2Cwspu%2Cwspv&time%3E=2023-09-20T00%3A00%3A00Z&time%3C=2023-09-27T14%3A52%3A00Z
/erddap/files/cwwcNDBCMet/.csv
/erddap/version
/erddap/tabledap/cwwcNDBCMet.nccsvMetadata
/erddap/files/cwwcNDBCMet/.csv
/erddap/tabledap/cwwcNDBCMet.nccsv?station,longitude,latitude&distinct()
/erddap/tabledap/cwwcNDBCMet.nccsv?station,longitude,latitude&distinct()
```

# Serving a static ERDDAP "remote dataset"

This caches responses from the "remote" ERDDAP for a few relevant requests
(version and nccsv/nccsvMetadata) and serves them as a fake/static
ERDDAP remote dataset which is proxied by the proxying ERDDAP.

After starting up the compose stack, run the following to cache
the proxied ERDDAP responses and restart the nginx-static and
erddap-proxy container to reload the static dataset.

```
./get_request_responses.sh
docker compose restart nginx-static erddap-proxy
```

Then the static dataset should be available for access on the proxying ERDDAP at
`/erddap/tabledap/cwwcNDBCMet-static.html`

# References

ERDDAP's `EDDTableFromERDDAP` which does various version checks
of the remote ERDDAP to identify how it should request data
from the remote dataset.

https://github.com/ERDDAP/erddap/blob/main/WEB-INF/classes/gov/noaa/pfel/erddap/dataset/EDDTableFromErddap.java

Noteable remote ERDDAP version implications:

* >=1.76: use .nccsv/.nccsvMetadata for communication with remote ERDDAP
* <1.75: use DAP for communication with remote ERDDAP
* >=2.10: remote /files supported
