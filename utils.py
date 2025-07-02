import openrouteservice
import time
from geopy.geocoders import Nominatim

# Initialize geolocator once
geolocator = Nominatim(user_agent="route-optimizer")

def geocode_address(address):
    """Geocode a single address into (latitude, longitude)."""
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")
    return (None, None)

def geocode_addresses(addresses):
    """Geocode a list of addresses into a list of (longitude, latitude)."""
    coords = []
    for i, address in enumerate(addresses):
        lat, lon = geocode_address(address)
        print(f"Geocoding [{i+1}/{len(addresses)}]: {address} => {lat}, {lon}")
        if lat is not None and lon is not None:
            coords.append((lon, lat))  # ORS expects (longitude, latitude)
        else:
            coords.append(None)
        time.sleep(1)  # Rate limiting
    return coords

def optimize_route_ors(coords, ors_api_key):
    """Optimize route with OpenRouteService.

    Args:
        coords: List of (longitude, latitude) tuples.
        ors_api_key: Your ORS API key string.

    Returns:
        Ordered dict of job_id to location if successful, else None.
    """
    try:
        client = openrouteservice.Client(key=ors_api_key)

        if len(coords) < 3:
            print("❌ You must provide at least 3 coordinates (start, 1 stop, end).")
            return None

        start = coords[0]
        end = coords[-1]
        jobs = [{"id": i+1, "location": loc} for i, loc in enumerate(coords[1:-1])]

        if not jobs:
            print("❌ No intermediate stops found (jobs list is empty).")
            return None

        vehicle = {
            "id": 1,
            "start": start,
            "end": end,
        }

        print("🔍 ORS optimization request:")
        print("Start:", start)
        print("End:", end)
        print("Jobs:", jobs)

        result = client.optimization(jobs=jobs, vehicles=[vehicle])

        steps = result["routes"][0]["steps"]
        print("✅ ORS Response OK")

        job_order = {step["id"]: step["location"] for step in steps}
        return job_order

    except openrouteservice.exceptions.ApiError as e:
        print("❌ ORS API Error:", e)
        return None
    except Exception as e:
        print("❌ Unexpected error:", e)
        return None
