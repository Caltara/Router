import streamlit as st
import pandas as pd
from utils import geocode_addresses, optimize_route_ors

st.set_page_config(page_title="AI Route Optimizer", layout="wide")
st.title("🚚 AI Route Optimizer (OpenRouteService)")
st.write("Upload a CSV with either:")
st.markdown("- ✅ `address` column (we'll geocode for you), **OR**")
st.markdown("- ✅ `latitude` and `longitude` columns (skip geocoding)")

uploaded_file = st.file_uploader("📤 Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Determine input method
    use_geocoding = False
    coords = []

    if "address" in df.columns:
        use_geocoding = True
        st.info("Detected `address` column. Geocoding will be used.")
        addresses = df["address"].tolist()
    elif "latitude" in df.columns and "longitude" in df.columns:
        st.success("Detected `latitude` and `longitude` columns. Skipping geocoding.")
        coords = list(zip(df["longitude"], df["latitude"]))
    else:
        st.error("CSV must contain either an `address` column OR both `latitude` and `longitude` columns.")
        st.stop()

    if len(df) < 2:
        st.warning("At least two locations are required.")
        st.stop()

    if st.button("🧠 Optimize Route"):
        with st.spinner("Optimizing..."):

            # If using geocoding, fetch coordinates
            if use_geocoding:
                coords = geocode_addresses(addresses)
                if None in coords:
                    st.error("Some addresses failed to geocode. Please check and try again.")
                    st.stop()

            # Optimize the route using OpenRouteService
            ors_api_key = st.secrets["ors"]["api_key"]
            order_dict = optimize_route_ors(coords, ors_api_key)

            if order_dict:
                # Reconstruct ordered list
                ordered_coords = [coords[0]]
                ordered_labels = [df.iloc[0]["address"] if use_geocoding else f"{coords[0][1]}, {coords[0][0]}"]

                for step in order_dict.values():
                    index = coords.index(step)
                    label = df.iloc[index]["address"] if use_geocoding else f"{step[1]}, {step[0]}"
                    ordered_coords.append(step)
                    ordered_labels.append(label)

                ordered_coords.append(coords[-1])
                end_label = df.iloc[-1]["address"] if use_geocoding else f"{coords[-1][1]}, {coords[-1][0]}"
                ordered_labels.append(end_label)

                df_out = pd.DataFrame({
                    "Stop Number": list(range(1, len(ordered_labels) + 1)),
                    "Location": ordered_labels
                })

                if "stop_time_minutes" in df.columns:
                    stop_times = []
                    for label in ordered_labels:
                        match = df[df["address"] == label] if use_geocoding else df[
                            (df["latitude"].astype(str) + ", " + df["longitude"].astype(str)) == label
                        ]
                        stop_times.append(match["stop_time_minutes"].values[0] if not match.empty else None)
                    df_out["Stop Time (min)"] = stop_times

                st.subheader("📍 Optimized Route")
                st.dataframe(df_out, use_container_width=True)

                st.download_button(
                    label="📄 Download Optimized Route CSV",
                    data=df_out.to_csv(index=False),
                    file_name="optimized_route.csv",
                    mime="text/csv"
                )
            else:
                st.error("Failed to optimize the route using OpenRouteService.")
