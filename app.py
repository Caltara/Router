import streamlit as st
from utils import optimize_route_ors

st.set_page_config(page_title="Route Optimizer Test", layout="wide")
st.title("🔧 ORS Route Optimizer – Test Mode")

st.write("This version skips file upload and uses hardcoded coordinates.")

# ✅ Hardcoded known-good coordinates (lon, lat)
coords = [
    (-122.0841, 37.4221),   # Google HQ
    (-122.0312, 37.3318),   # Apple HQ
    (-122.3961, 37.7862)    # SF Ferry Building
]

st.write("📍 Coordinates being sent to ORS:")
st.code(coords)

# Round-trip option
round_trip = st.checkbox("🔁 Return to start", value=True)
if round_trip:
    coords.append(coords[0])

if st.button("🧠 Optimize Route"):
    with st.spinner("Calling ORS..."):
        ors_api_key = st.secrets["ors"]["api_key"]
        result = optimize_route_ors(coords, ors_api_key)

        if result:
            st.success("✅ ORS optimization succeeded.")
            st.write("📋 Ordered steps:")
            st.json(result)
        else:
            st.error("❌ ORS optimization failed. See logs for details.")
