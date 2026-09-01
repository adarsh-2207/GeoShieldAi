# GeoShield AI — V1 Methodology

## 1. Objective

GeoShield V1 estimates **spatial mine-collapse risk** at sampled locations in the Jharia Coalfield using environmental and satellite-derived features.

The model is intended as a research prototype and does not predict the exact time of a collapse.

## 2. Region

The current application uses a Jharia Coalfield bounding box:

- Longitude: 86.1–86.5
- Latitude: 23.6–23.9

## 3. Feature engineering

### NDVI

NDVI is calculated from Sentinel-2 near-infrared and red bands:

```text
NDVI = (NIR - Red) / (NIR + Red)
```

GeoShield compares a 2017 baseline with 2025 imagery.

```text
NDVI Change = NDVI_2025 - NDVI_2017
```

This is used as a proxy for long-term vegetation/land-condition change.

### Elevation

SRTM DEM provides terrain elevation.

### Rainfall

ERA5-Land monthly precipitation is aggregated over the selected historical period to produce a cumulative rainfall feature.

### Current NDVI

The 2025 Sentinel-2 NDVI value represents current vegetation condition.

## 4. V1 feature matrix

The model receives:

```text
[
    ndvi_change,
    elevation,
    rainfall,
    ndvi_2025
]
```

The serialized model confirms four input features and 100 Random Forest trees.

## 5. Training

The current model was trained using 20 labeled Jharia locations:

- 10 collapse/subsidence points
- 10 safe points

The labels were assembled from project research material and published/government sources.

Because the training set is small, the model should be treated as a proof of concept rather than a validated operational predictor.

## 6. Inference

For each sampled point:

1. Satellite/environmental features are extracted.
2. Features are passed to the trained Random Forest.
3. `predict_proba()` is used to obtain the high-risk-class score.
4. The score is displayed on the map.
5. A configurable threshold separates high-risk and safe sampled points.

## 7. Visualization

The application provides:

- Interactive Folium risk map
- Risk-score distribution
- Random Forest feature importance
- High-risk location table
- CSV export

## 8. Why Random Forest?

Random Forest was selected for V1 because it:

- handles nonlinear feature relationships,
- works naturally with mixed-scale tabular features,
- provides feature-importance estimates,
- is relatively interpretable,
- is practical for a small proof-of-concept dataset.

## 9. Important methodological limitations

The current V1 does not yet provide:

- independent geographic holdout validation,
- temporal holdout validation,
- calibrated probabilities,
- uncertainty intervals,
- a large independently verified ground-truth dataset,
- time-to-collapse forecasting.

These are core targets for V2.
