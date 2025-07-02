import streamlit as st
import pandas as pd
from utils import optimize_route_ors

st.set_page_config(page_title="Route Optimizer", layout="wide")
st.title("🚚 AI Route Optimizer (OpenRouteService)")
st.write("Upload a CSV with at least `latitude` and `longitude` columns.")

uploaded_file = st.file_uploader("📤 Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if not {"latitude", "longitude"}.issubset(df.columns):
        st.error("Your CSV must contain `latitude` and `longitude` columns.")
        st.stop()

    if len(df) < 2:
        st.error("You must provide at least 2 locations (start + 1 stop).")
        st.stop()

    round_trip = st.checkbox("🔁 Return to start location", value=True)

    coords = list(zip(df["longitude"], df["latitude"]))

    if round_trip:
        coords.append(coords[0])  # Add start again as end

    if st.button("🧠 Optimize Route"):
        with st.spinner("Optimizing..."):
            ors_api_key = st.secrets["ors"]["api_key"]
            route = optimize_route_ors(coords, ors_api_key)

            if route is None:
                st.error("❌ Failed to optimize route using OpenRouteService.")
            else:
                # Reconstruct the ordered list
                ordered_coords = [coords[0]]
                ordered_labels = [f"{df.iloc[0]['First Name']} {df.iloc[0]['Last Name']}"]

                for step in route.values():
                    index = coords.index(step)
                    label = f"{df.iloc[index]['First Name']} {df.iloc[index]['Last Name']}"
                    ordered_coords.append(step)
                    ordered_labels.append(label)

                if round_trip:
                    ordered_coords.append(coords[0])
                    ordered_labels.append(f"{df.iloc[0]['First Name']} {df.iloc[0]['Last Name']}")

                df_out = pd.DataFrame({
                    "Stop #": list(range(1, len(ordered_labels) + 1)),
                    "Name": ordered_labels
                })

                st.success("✅ Route optimized successfully!")
                st.dataframe(df_out, use_container_width=True)

                st.download_button(
                    label="📄 Download Route CSV",
                    data=df_out.to_csv(index=False),
                    file_name="optimized_route.csv",
                    mime="text/csv"
                )
