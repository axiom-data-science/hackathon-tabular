from fastapi import Depends, FastAPI, HTTPException, Request
import pandas as pd
from urllib.parse import urlparse, unquote
from typing import Tuple
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastapi.responses import PlainTextResponse
from pathlib import Path
from typing import Annotated, NamedTuple
import time
import io
import csv
import re
import os
import xarray as xr
import numpy as np



class Constraint(NamedTuple):
    key: str
    operator: str
    value: str


app = FastAPI()

if os.environ.get("ENABLE_CORS"):
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class CsvResponse(PlainTextResponse):
    media_type = "text/csv;charset=UTF-8"


app = FastAPI()


dtype_to_erddap = {
    np.dtype('float64'): 'double',
    np.dtype('float32'): 'float',
    np.dtype('int32'): 'int',
    np.dtype('M8[ns]'): 'String',
    np.dtype('object'): 'String',
}


def map_value_to_csv(nckey, key, value, buf, writer):
    if nckey is None:
        nckey = '*GLOBAL*'
    if isinstance(value, str):
        if '\n' in value:
            value = value.replace('\n', '\\n')
        if re.match(r'\d+', value):
            buf.write(f'{nckey},{key},"{value}"\n')
        else:
            writer.writerow([nckey,key, value])
    if isinstance(value, (int, np.integer)):
        buf.write(f'{nckey},{key},{value}i\n')
    if isinstance(value, (float, np.floating)):
        buf.write(f'{nckey},{key},{value}d\n')


@app.get("/")
async def redirect():
    """Default page will redirect the user to the api docs."""
    response = RedirectResponse(url="/docs")
    return response


@app.get("/erddap/version", response_class=PlainTextResponse)
async def get_erddap_version() -> PlainTextResponse:
    return "ERDDAP_version=2.23"


def _open_dataset_nc(dataset_id: str) -> xr.Dataset:
    pth = Path(f'datasets/{dataset_id}.nc')
    if not pth.exists():
        raise HTTPException(status_code=404, detail="No such dataset")
    print(pth)
    return xr.open_dataset(str(pth))


def _get_nccsv_metadata(ds: xr.Dataset) -> str:
    buf = io.StringIO()

    writer = csv.writer(buf)

    #add required Conventions global attribute
    map_value_to_csv(None, 'Conventions', 'COARDS, CF-1.6, ACDD-1.3, NCCSV-1.2', buf, writer)

    for key, value in ds.attrs.items():
        map_value_to_csv(None, key, value, buf, writer)

    for varname in ds.variables:
        for dtype, erddap_dtype in dtype_to_erddap.items():
            if np.issubdtype(ds[varname].dtype, dtype):
                map_value_to_csv(varname, '*DATA_TYPE*', erddap_dtype, buf, writer)
                break
        else:
            raise ValueError(f'Unsupported dtype: {varname} {ds[varname].dtype}')
        for key, value in ds[varname].attrs.items():
            if varname == "time" and key in ("units", "time_origin"):
                continue
            map_value_to_csv(varname, key, value, buf, writer)
        if varname == "time":
            map_value_to_csv(varname, "units", "yyyy-MM-dd'T'HH:mm:ssZ", buf, writer)
            map_value_to_csv(varname, "time_origin", "01-JAN-1970 00:00:00", buf, writer)

    buf.write('\n*END_METADATA*\n')
    buf.seek(0)
    return buf.read()


@app.get("/erddap/tabledap/{dataset_id}.nccsvMetadata", response_class=CsvResponse)
async def get_nccsv_metadata(dataset_id) -> CsvResponse:
    ds = _open_dataset_nc(dataset_id)
    return _get_nccsv_metadata(ds)


@app.get("/erddap/tabledap/{dataset_id}.nccsv", response_class=CsvResponse)
async def get_nccsv(dataset_id, request: Request):
    ds = _open_dataset_nc(dataset_id)
    metadata_header = _get_nccsv_metadata(ds)
    params = request.query_params
    url = str(request.url)
    constraints = []
    fields = None

    if '?' in url:
        parts = urlparse(url)
        decoded_qs = unquote(parts.query)
        query_args = decoded_qs.split('&')
        fields = query_args[0].split(',')
        for query in query_args[1:]:
            if any([i in query for i in '=><']):
                constraints.append(parse_constraint(query))

    if fields:
        for field in fields:
            if field not in ds.variables:
                raise HTTPException(status_code=400, detail=f"Invalid variable: {field}")
        ds = ds[fields]
    else:
        fields = list(ds.variables)
    if fields:
        csv_body = fields2frame(ds, fields).iloc[:10].to_csv(index=False)
    else:
        csv_body = ds.drop_dims('timeseries').to_pandas().iloc[:10].to_csv(index=False)
    body = metadata_header + csv_body
    return body


@app.get("/erddap/version", response_class=PlainTextResponse)
async def get_erddap_version():
    return "ERDDAP_version=2.23\n"


@app.get("/erddap/files/{dataset_id}/.csv", response_class=CsvResponse)
async def get_files(dataset_id):
    timestamp = int(time.time()*1000)
    body = (
        'Name,Last modified,Size,Description\n'
        f'{dataset_id}.nc,1695844880992,670238'
    )
    return body


def parse_constraint(constraint: str) -> Constraint:
    operators = [
        '>=',
        '>',
        '<=',
        '<',
        '=',
    ]
    for operator in operators:
        if operator in constraint:
            key, value = constraint.split(operator)
            return Constraint(key, operator, value)
    else:
        raise ValueError('Not a parseable constraint')


def fields2frame(ds, fields):
    frame = {}
    for field in fields:
        frame[field] = ds[field].to_numpy()

    maxlen = 1
    for dim in ds.dims:
        maxlen = max(maxlen, ds.dims[dim])
    arrlen = maxlen

    for field, arr in frame.items():
        if len(arr) == 1:
            dtype = arr.dtype
            long_arr = np.empty(arrlen, dtype=dtype)
            long_arr[:] = arr[0]
            frame[field] = long_arr
        if field == "time":
            long_arr = np.datetime_as_string(arr.astype('M8[s]'), timezone='UTC')
            frame[field] = long_arr
    return pd.DataFrame(frame)
