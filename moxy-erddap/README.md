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
uvicorn app:app --host 0.0.0.0
```

Bootstrapping
-------------

```
mkdir datasets
wget http://files.axds.co/ioos-dmac-2023/gov_noaa_knsi_flat.nc -O datasets/example.nc
wget -P datasets/ https://raw.githubusercontent.com/ioos/erddap-gold-standard/master/datasets/edu_calpoly_marine_morro_bay_met.nc
wget -P datasets/ https://raw.githubusercontent.com/ioos/erddap-gold-standard/master/datasets/org_cormp_cap2.nc
wget -P datasets/ https://raw.githubusercontent.com/ioos/erddap-gold-standard/master/datasets/usf_comps_c10_inwater.nc
```
