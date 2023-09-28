from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastapi.responses import PlainTextResponse
from pathlib import Path
from typing import Annotated
import io
import csv
import re
import os
import xarray as xr
import numpy as np


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


@app.get("/erddap/tabledap/{dataset_id}.nccsvMetadata", response_class=CsvResponse)
async def get_nccsv_metadata(dataset_id) -> CsvResponse:
    pth = Path(f'datasets/{dataset_id}.nc')
    if not pth.exists():
        raise HTTPException(status_code=404, detail="No such dataset")
    print(pth)
    ds = xr.open_dataset(str(pth))
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
            map_value_to_csv(varname, key, value, buf, writer)
    buf.write('\n*END_METADATA*\n')
    buf.seek(0)
    return buf.read()


@app.get("/erddap/tabledap/{dataset_id}.nccsv", response_class=CsvResponse)
async def get_nccsv(dataset_id, request: Request):
    pth = Path(f'datasets/{dataset_id}.nc')
    if not pth.exists():
        raise HTTPException(status_code=404, detail="No such dataset")
    print(pth)
    ds = xr.open_dataset(str(pth))
    buf = io.StringIO()

    writer = csv.writer(buf)

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
            map_value_to_csv(varname, key, value, buf, writer)
    buf.write('\n*END_METADATA*\n')
    buf.seek(0)
    metadata_header =  buf.read()
    csv_body = ds.drop_dims('timeseries').to_pandas().iloc[:10].to_csv()
    body = metadata_header + csv_body
    return body
