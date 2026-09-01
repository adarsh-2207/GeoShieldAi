# GeoShield AI — System Architecture

## V1 architecture

```mermaid
flowchart TD
    A[Google Earth Engine] --> B[Data Acquisition]

    B --> S2[Sentinel-2]
    B --> DEM[SRTM DEM]
    B --> R[ERA5-Land]

    S2 --> F1[NDVI 2017]
    S2 --> F2[NDVI 2025]
    F1 --> F3[NDVI Change]
    F2 --> F3

    DEM --> F4[Elevation]
    R --> F5[Cumulative Rainfall]
    F2 --> F6[Current NDVI]

    F3 --> X[Feature Matrix]
    F4 --> X
    F5 --> X
    F6 --> X

    X --> M[Random Forest Classifier]
    M --> P[Risk Score 0–1]

    P --> V[Streamlit Application]
    V --> MAP[Folium Interactive Risk Map]
    V --> CHART[Risk Distribution]
    V --> IMP[Feature Importance]
    V --> CSV[High-Risk CSV Export]
```

## Components

| Layer | Component | Role |
|---|---|---|
| Data | Google Earth Engine | Cloud-side geospatial data access/processing |
| Optical imagery | Sentinel-2 | NDVI and vegetation-change features |
| Terrain | SRTM DEM | Elevation feature |
| Climate | ERA5-Land | Cumulative rainfall feature |
| ML | Random Forest | Spatial risk classification |
| Backend/application | Python | Data processing and inference |
| UI | Streamlit | Interactive application |
| Mapping | Folium | Risk-map visualization |
| Output | CSV | Export of high-risk sampled locations |

## Inference flow

```text
User selects sample count + risk threshold
                    ↓
        Google Earth Engine query
                    ↓
           Feature extraction
                    ↓
             Spatial sampling
                    ↓
         Pandas feature dataframe
                    ↓
          Random Forest inference
                    ↓
          Risk score for each point
                    ↓
       Map + charts + high-risk table
                    ↓
               CSV export
```

## V2 direction

The planned V2 architecture adds:

```text
Sentinel-1 SAR / InSAR
Landsat thermal anomalies
Expanded ground truth
Temporal features
Weather updates
        ↓
Improved validation + model
        ↓
Calibrated risk / uncertainty
        ↓
Trend detection + alerts
```

V2 should be treated as a separate development phase rather than represented as completed functionality in the V1 repository.
