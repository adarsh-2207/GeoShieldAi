import os
from pathlib import Path

import streamlit as st
import ee
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from geemap import ee_to_df

# Initialize Google Earth Engine and load the V1 model
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "geoshield_model.pkl"
SAMPLE_MAP_PATH = BASE_DIR / "outputs" / "geoshield_risk_map.png"

GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID")
if not GEE_PROJECT_ID:
    st.error(
        "GEE_PROJECT_ID is not set. Set it to your Google Cloud / Earth Engine project ID "
        "after authenticating with Google Earth Engine."
    )
    st.stop()

try:
    ee.Initialize(project=GEE_PROJECT_ID)
except Exception as exc:
    st.error(
        "Google Earth Engine could not be initialized. Run `earthengine authenticate` "
        "and verify that GEE_PROJECT_ID is correct."
    )
    st.exception(exc)
    st.stop()

model = joblib.load(MODEL_PATH)

st.set_page_config(
    page_title="GeoShield AI",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #e94560;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        color: white;
        margin: 0;
    }
    .main-subtitle {
        font-size: 1.1rem;
        color: #a0aec0;
        margin-top: 0.5rem;
    }
    .stat-card-red {
        background: linear-gradient(135deg, #c0392b, #e74c3c);
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .stat-card-green {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .stat-card-blue {
        background: linear-gradient(135deg, #2980b9, #3498db);
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .stat-card-orange {
        background: linear-gradient(135deg, #e67e22, #f39c12);
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
    }
    .stat-label {
        font-size: 0.85rem;
        opacity: 0.9;
        margin: 0;
    }
    .alert-box {
        background: linear-gradient(135deg, #c0392b, #e74c3c);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e94560;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="main-header">
    <p class="main-title">🛡️ GeoShield AI</p>
    <p class="main-subtitle">
        AI-powered Mine Collapse Risk Mapping Prototype — Jharia Coalfield<br>
        <span style="color: #e94560;">🛰️ Sentinel-2 Satellite &nbsp;|&nbsp; 🌍 Google Earth Engine &nbsp;|&nbsp; 🤖 Random Forest ML &nbsp;|&nbsp; 📅 8 Years of Data</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Problem statement
st.markdown("""
<div class="info-box">
    <b style="color: #e94560; font-size: 1.1rem;">⚠️ The Problem</b><br>
    <span style="color: #a0aec0;">
    Over <b style="color:white;">5 lakh people</b> live in high-risk mine collapse zones across India's coalfields. 
    Current monitoring is <b style="color:white;">manual, slow, and reactive</b>. 
    GeoShield uses 8 years of satellite data to estimate spatial collapse-risk scores <b style="color:white;">from satellite-derived features</b>.
    </span>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🛡️ GeoShield Controls")
st.sidebar.markdown("---")

region = st.sidebar.selectbox(
    "🗺️ Select Coalfield",
    ["Jharia, Jharkhand", "Raniganj, West Bengal (Coming Soon)"]
)

num_points = st.sidebar.slider("📍 Sample Points", 100, 500, 300)
risk_threshold = st.sidebar.slider("⚠️ Risk Threshold", 0.0, 1.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**📡 Data Sources**
- Sentinel-2 (ESA)
- SRTM DEM (USGS)  
- ERA5 Rainfall (ECMWF)

**🤖 Model**
- Random Forest Classifier
- 4 Features
- Trained on Jharia Coalfield
""")

# Region
if "Coming Soon" in region:
    st.warning("🔜 Raniganj data coming soon! Please select Jharia for now.")
    st.stop()

area = ee.Geometry.Rectangle([86.1, 23.6, 86.5, 23.9])
center = [23.75, 86.25]

# Run button
if st.button("🔍 Run Risk Analysis", type="primary", use_container_width=True):
    with st.spinner("🛰️ Fetching satellite data and running AI analysis... This may take 30-60 seconds"):

        ndvi_2017 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
            .filterBounds(area).filterDate('2017-01-01', '2018-01-01') \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
            .median().normalizedDifference(['B8', 'B4']).rename('ndvi_2017')

        ndvi_2025 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
            .filterBounds(area).filterDate('2025-01-01', '2026-01-01') \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
            .median().normalizedDifference(['B8', 'B4']).rename('ndvi_2025')

        ndvi_change = ndvi_2025.subtract(ndvi_2017).rename('ndvi_change')
        dem = ee.Image('USGS/SRTMGL1_003').clip(area).rename('elevation')
        rainfall = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR') \
            .filterBounds(area).filterDate('2017-01-01', '2025-12-31') \
            .select('total_precipitation_sum').sum().clip(area).rename('rainfall')

        combined = ndvi_change.addBands(dem).addBands(rainfall).addBands(ndvi_2025)

        random_points = combined.sample(
            region=area, scale=100, numPixels=num_points, seed=42, geometries=True
        )

        df_map = ee_to_df(random_points, remove_geom=False)
        df_map = df_map.drop(columns=['geo']) if 'geo' in df_map.columns else df_map

        coords = random_points.getInfo()['features']
        df_map['lat'] = [f['geometry']['coordinates'][1] for f in coords]
        df_map['lon'] = [f['geometry']['coordinates'][0] for f in coords]

        X = df_map[['ndvi_change', 'elevation', 'rainfall', 'ndvi_2025']]
        df_map['risk'] = model.predict_proba(X)[:, 1]
        df_map['risk_level'] = df_map['risk'].apply(
            lambda x: '🔴 High Risk' if x > risk_threshold else '🟢 Safe'
        )

    high_risk_count = (df_map['risk'] > risk_threshold).sum()
    safe_count = (df_map['risk'] <= risk_threshold).sum()
    avg_risk = df_map['risk'].mean()
    max_risk = df_map['risk'].max()

    # Alert if very high risk
    if max_risk > 0.85:
        st.markdown(f"""
        <div class="alert-box">
            🚨 CRITICAL ALERT: {(df_map['risk'] > 0.85).sum()} zones detected with risk score above 85% — Immediate attention required!
        </div>
        """, unsafe_allow_html=True)

    # Metric cards
    st.markdown("### 📊 Analysis Results")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card-blue">
            <p class="stat-number">{len(df_map)}</p>
            <p class="stat-label">Total Points Analyzed</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card-red">
            <p class="stat-number">{high_risk_count}</p>
            <p class="stat-label">🔴 High Risk Zones</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card-green">
            <p class="stat-number">{safe_count}</p>
            <p class="stat-label">🟢 Safe Zones</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card-orange">
            <p class="stat-number">{avg_risk:.2f}</p>
            <p class="stat-label">⚠️ Avg Risk Score</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Map + Chart
    col_map, col_chart = st.columns([2, 1])

    with col_map:
        st.markdown("### Live Risk Map — Jharia Coalfield")
        m = folium.Map(location=center, zoom_start=11, tiles='CartoDB dark_matter')
        for _, row in df_map.iterrows():
            color = 'red' if row['risk'] > risk_threshold else 'green'
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=6,
                color=color,
                fill=True,
                fill_opacity=0.8,
                popup=folium.Popup(f"<b>Risk Score: {row['risk']:.2f}</b><br>Elevation: {row['elevation']:.0f}m<br>Status: {row['risk_level']}", max_width=200)
            ).add_to(m)
        st_folium(m, width=700, height=500, returned_objects=[])

    with col_chart:
        st.markdown("### 📈 Risk Distribution")
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#16213e')
        ax.hist(df_map['risk'], bins=20, color='#e94560', alpha=0.8, edgecolor='white', linewidth=0.5)
        ax.axvline(risk_threshold, color='yellow', linestyle='--', linewidth=2, label=f'Threshold ({risk_threshold})')
        ax.set_xlabel('Risk Score', color='white')
        ax.set_ylabel('Count', color='white')
        ax.set_title('Risk Score Distribution', color='white')
        ax.tick_params(colors='white')
        ax.legend(facecolor='#1a1a2e', labelcolor='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#e94560')
        st.pyplot(fig)

        # Feature importance
        st.markdown("### 🔬 Feature Importance")
        features = ['NDVI Change', 'Elevation', 'Rainfall', 'NDVI 2025']
        importance = model.feature_importances_
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        fig2.patch.set_facecolor('#1a1a2e')
        ax2.set_facecolor('#16213e')
        bars = ax2.barh(features, importance, color=['#e94560', '#3498db', '#2ecc71', '#f39c12'])
        ax2.set_xlabel('Importance', color='white')
        ax2.tick_params(colors='white')
        for spine in ax2.spines.values():
            spine.set_edgecolor('#e94560')
        st.pyplot(fig2)

    # Table
    st.markdown("### 📋 High Risk Locations")
    high_risk_df = df_map[df_map['risk'] > risk_threshold][['lat', 'lon', 'risk', 'elevation', 'ndvi_change', 'risk_level']]
    high_risk_df = high_risk_df.sort_values('risk', ascending=False).reset_index(drop=True)
    st.dataframe(high_risk_df, use_container_width=True)

    csv = high_risk_df.to_csv(index=False)
    st.download_button("⬇️ Download High Risk Zones CSV", csv, "geoshield_risk_zones.csv", "text/csv")

    # About section
    st.markdown("---")
    st.markdown("""
    <div class="info-box">
        <b style="color: #e94560; font-size: 1.1rem;">🔬 How GeoShield Works</b><br><br>
        <span style="color: #a0aec0;">
        <b style="color:white;">1. Satellite Data Fetch</b> — Downloads 8 years of Sentinel-2 imagery from Google Earth Engine<br>
        <b style="color:white;">2. Feature Extraction</b> — Calculates NDVI change, elevation, and rainfall for each location<br>
        <b style="color:white;">3. AI Prediction</b> — Random Forest model assigns a collapse risk score (0-1) to each zone<br>
        <b style="color:white;">4. Risk Map</b> — Visualizes predictions on an interactive map for decision makers<br><br>
        </span>
    </div>
    """, unsafe_allow_html=True)

else:
    st.image(str(SAMPLE_MAP_PATH), caption="Sample Risk Map - Jharia Coalfield", use_container_width=True)
    st.markdown("""
    <div class="info-box">
        <b style="color: #e94560;">👆 Click 'Run Risk Analysis' to start live satellite analysis</b><br>
        <span style="color: #a0aec0;">Analysis fetches real-time data from Google Earth Engine and may take 30-60 seconds.</span>
    </div>
    """, unsafe_allow_html=True) 
    ## Have you considerd the factor that jaria is constantly burning for around 115 years??
