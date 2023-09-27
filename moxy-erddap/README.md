Install
-------

```
conda env update
```

Running
-------

```
uvicorn app:app
```

or if you're running non-locally and need to serve on all interfaces:

```
unvicorn app:app --host 0.0.0.0
```

Bootstrapping
-------------

```
mkdir datasets
wget http://files.axds.co/ioos-dmac-2023/gov_noaa_knsi_flat.nc -O datasets/example.nc
```
