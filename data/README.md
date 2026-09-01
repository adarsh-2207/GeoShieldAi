# Data

Raw satellite and climate datasets are **not stored in this repository**.

GeoShield retrieves the required datasets through Google Earth Engine:

- Sentinel-2
- SRTM DEM
- ERA5-Land

This keeps the repository lightweight and avoids committing large remote-sensing datasets.

The current trained model is stored separately in:

```text
models/geoshield_model.pkl
```

Do not commit credentials, service-account files, private datasets, or `.env` files.
