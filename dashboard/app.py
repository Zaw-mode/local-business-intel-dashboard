"""Streamlit dashboard for Austin Coffee & Juice Intelligence."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import joblib
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from acji.config import get_settings
from acji.utils.geo import haversine_distance_m


st.set_page_config(page_title="ACJI Dashboard", page_icon="☕", layout="wide")

settings = get_settings()


@st.cache_data(show_spinner=False)
def load_data(duckdb_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not duckdb_path.exists():
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    with duckdb.connect(str(duckdb_path)) as conn:
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}

        shops = (
            conn.execute("SELECT * FROM shops_master").df() if "shops_master" in tables else pd.DataFrame()
        )
        cheapest = (
            conn.execute("SELECT * FROM analytics_cheapest_shops").df()
            if "analytics_cheapest_shops" in tables
            else pd.DataFrame()
        )
        opportunities = (
            conn.execute("SELECT * FROM analytics_market_opportunity").df()
            if "analytics_market_opportunity" in tables
            else pd.DataFrame()
        )

    return shops, cheapest, opportunities


@st.cache_resource(show_spinner=False)
def load_model(model_path: Path):
    if model_path.exists():
        return joblib.load(model_path)
    return None



def estimate_nearby_competition(df: pd.DataFrame, lat: float, lon: float, radius_m: float = 1200) -> int:
    if df.empty:
        return 0

    count = 0
    for row in df.itertuples(index=False):
        distance = haversine_distance_m(lat, lon, float(row.latitude), float(row.longitude))
        if distance <= radius_m:
            count += 1
    return count



def heuristic_revenue_prediction(price_tier: float, rating: float, reviews: int, traffic_proxy: float) -> float:
    return float(500 + (rating * 140) + (np.log1p(reviews) * 220) + (traffic_proxy * 900) + ((5 - price_tier) * 70))



def build_feature_row(
    lat: float,
    lon: float,
    price_tier: float,
    rating: float,
    reviews: int,
    traffic_proxy: float,
    source_count: int,
    overall_score: float,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "latitude": lat,
                "longitude": lon,
                "price_tier": price_tier,
                "rating": rating,
                "review_count": reviews,
                "traffic_proxy": traffic_proxy,
                "source_count": source_count,
                "overall_score": overall_score,
            }
        ]
    )


shops_df, cheapest_df, opportunities_df = load_data(settings.duckdb_path)
model = load_model(settings.model_artifact_path)

st.title("Austin Coffee & Juice Intelligence (ACJI)")
st.caption("Rankings combine affordability and traffic-proxy signals from OSM Overpass, Nominatim, and Foursquare.")

if shops_df.empty:
    st.warning("No data found yet. Run `python scripts/run_pipeline.py` first.")
    st.stop()

price_col = "price_tier_imputed" if "price_tier_imputed" in shops_df.columns else "price_tier"
rating_col = "rating_imputed" if "rating_imputed" in shops_df.columns else "rating"
reviews_col = "review_count_imputed" if "review_count_imputed" in shops_df.columns else "review_count"

with st.sidebar:
    st.header("Filters")

    price_range = st.slider("Price tier", min_value=1.0, max_value=4.0, value=(1.0, 4.0), step=0.5)
    min_rating = st.slider("Minimum rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
    min_reviews = st.slider("Minimum reviews", min_value=0, max_value=1000, value=0, step=10)
    source_count_filter = st.slider("Minimum source coverage", min_value=1, max_value=3, value=1)
    sort_metric = st.selectbox("Sort by", ["overall_score", "price_tier", "traffic_proxy", "rating"])

sort_col_map = {
    "overall_score": "overall_score",
    "price_tier": price_col,
    "traffic_proxy": "traffic_proxy",
    "rating": rating_col,
}
sort_col = sort_col_map[sort_metric]

filtered = shops_df[
    (shops_df[price_col].fillna(2.5) >= price_range[0])
    & (shops_df[price_col].fillna(2.5) <= price_range[1])
    & (shops_df[rating_col].fillna(0.0) >= min_rating)
    & (shops_df[reviews_col].fillna(0).astype(int) >= min_reviews)
    & (shops_df["source_count"].fillna(1).astype(int) >= source_count_filter)
].copy()

filtered["display_price_tier"] = filtered[price_col].fillna(2.5)
filtered["display_rating"] = filtered[rating_col].fillna(3.5)
filtered["display_reviews"] = filtered[reviews_col].fillna(0).astype(int)

ascending = sort_metric == "price_tier"
filtered = filtered.sort_values(by=sort_col, ascending=ascending)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Filtered shops", len(filtered))
col2.metric("Avg price tier", round(filtered["display_price_tier"].mean(), 2) if not filtered.empty else 0)
col3.metric("Avg traffic proxy", round(filtered["traffic_proxy"].fillna(0).mean(), 3) if not filtered.empty else 0)
col4.metric("Avg overall score", round(filtered["overall_score"].fillna(0).mean(), 2) if not filtered.empty else 0)

st.subheader("Map")
if filtered.empty:
    st.info("No shops match the selected filters.")
else:
    midpoint = (float(filtered["latitude"].mean()), float(filtered["longitude"].mean()))
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        get_position="[longitude, latitude]",
        get_fill_color="[255 - price_score * 120, 120 + traffic_proxy * 120, 90, 180]",
        get_radius=90,
        pickable=True,
    )
    tooltip = {
        "html": "<b>{name}</b><br/>Price Tier: {display_price_tier}<br/>Rating: {display_rating}<br/>Traffic Proxy: {traffic_proxy}<br/>Overall Score: {overall_score}",
        "style": {"backgroundColor": "#1f2937", "color": "white"},
    }
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(latitude=midpoint[0], longitude=midpoint[1], zoom=11),
        tooltip=tooltip,
    )
    st.pydeck_chart(deck, use_container_width=True)

st.subheader("Ranked Shops")
preferred_cols = [
    "shop_id",
    "name",
    "category",
    "price_tier",
    "price_tier_imputed",
    "price_tier_source",
    "rating",
    "rating_imputed",
    "rating_source",
    "review_count",
    "review_count_imputed",
    "source_count",
    "traffic_proxy",
    "overall_score",
]
display_cols = [column for column in preferred_cols if column in filtered.columns]
st.dataframe(filtered[display_cols].head(200), use_container_width=True)

with st.expander("Scoring explanation"):
    st.markdown(
        """
- **Price Score (55%)**: lower price tier receives higher score.
- **Traffic Proxy (45%)**: weighted blend of review volume, average rating, and source coverage.
- **Overall Score**: `(0.55 * price_score + 0.45 * traffic_proxy) * 100`.
- **Price/Rating source columns** show whether values are observed from providers or imputed defaults.
- **Market Opportunity**: area-level signal favoring high demand and lower competition concentration.
"""
    )

st.subheader("Market Opportunity Areas")
if opportunities_df.empty:
    st.info("No opportunity table found yet. Run the pipeline to generate analytics tables.")
else:
    st.dataframe(opportunities_df.head(50), use_container_width=True)

st.subheader("Location Simulator")
left, right = st.columns(2)
with left:
    sim_lat = st.number_input("Latitude", value=30.2672, format="%.6f")
    sim_lon = st.number_input("Longitude", value=-97.7431, format="%.6f")
    sim_price = st.slider("Planned price tier", min_value=1.0, max_value=4.0, value=2.0, step=0.5)
with right:
    sim_rating = st.slider("Expected rating", min_value=1.0, max_value=5.0, value=4.2, step=0.1)
    sim_reviews = st.slider("Expected monthly reviews", min_value=0, max_value=1000, value=120, step=10)
    sim_traffic = st.slider("Traffic proxy assumption", min_value=0.0, max_value=1.0, value=0.55, step=0.01)

nearby_competitors = estimate_nearby_competition(shops_df, sim_lat, sim_lon)
raw_score = (0.55 * (1 - (sim_price - 1) / 3) + 0.45 * sim_traffic) * 100

feature_row = build_feature_row(
    lat=sim_lat,
    lon=sim_lon,
    price_tier=sim_price,
    rating=sim_rating,
    reviews=sim_reviews,
    traffic_proxy=sim_traffic,
    source_count=max(1, min(3, int(np.ceil(nearby_competitors / 30)) + 1)),
    overall_score=raw_score,
)

if model is not None:
    revenue_prediction = float(model.predict(feature_row)[0])
else:
    revenue_prediction = heuristic_revenue_prediction(
        price_tier=sim_price,
        rating=sim_rating,
        reviews=sim_reviews,
        traffic_proxy=sim_traffic,
    )

opportunity_indicator = revenue_prediction / (nearby_competitors + 1)

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Predicted monthly revenue (proxy)", f"${revenue_prediction:,.0f}")
metric2.metric("Nearby competitors (1.2km)", nearby_competitors)
metric3.metric("Opportunity indicator", f"{opportunity_indicator:,.1f}")

with st.expander("Simulation details"):
    st.code(json.dumps(feature_row.to_dict(orient="records")[0], indent=2), language="json")
