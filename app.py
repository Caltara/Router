import streamlit as st
import pandas as pd
from utils import geocode_addresses, optimize_route_ors
import time

st.set_page_config(page_title="AI Route Optimizer", layout="wide")
st.title("🚚 AI Route Optimizer (OpenRouteService)")
st.write("Upload a CSV with an `address` column (and optional `stop_time_minutes`) to get the shortest route.")

uploaded_file = st.file_uploader("📤 Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "address" not in df.columns:
        st.error("CSV must have an `address` column.")
    else:
        st.success(f"{len(df)} addresses loaded.")
        addresses = df["address"].tolist()

        if len(addresses) < 2:
            st.warning("At least two addresses are required.")
        else:
            if st.button("🧠 Optimize Route"):
                with st.spinner("Geocoding and optimizing..."):
                    coords = geocode_addresses(addresses)

                    if None in coords:
                        st.error("Failed to geocode some addresses.")
                    else:
                        ors_api_key = st.secrets["ors"]["api_key"]
                        order_dict = optimize_route_ors(coords, ors_api_key)

                        if order_dict:
                            ordered_coords = [coords[0]]  # start
                            ordered_addresses = [addresses[0]]

                            for step in order_dict.values():
                                index = coords.index(step)
                                ordered_coords.append(step)
                                ordered_addresses.append(addresses[index])

                            ordered_coords.append(coords[-1])
                            ordered_addresses.append(addresses[-1])

                            df_out = pd.DataFrame({
                                "Stop Number": list(range(1, len(ordered_addresses) + 1)),
                                "Address": ordered_addresses
                            })

                            if "stop_time_minutes" in df.columns:
                                stop_times = [df[df["address"] == addr]["stop_time_minutes"].values[0] if addr in df["address"].values else None for addr in ordered_addresses]
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
                            st.error("Failed to optimize the route using ORS.")
