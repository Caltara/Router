import openrouteservice
import time
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="route-optimizer")

def geocode_address(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
    except:
        return (None, None)
    return (None, None)

def geocode_addresses(addresses):
    coords = []
    for i, address in enumerate(addresses):
        lat, lon = geocode_address(address)
        print(f"Geocoding [{i+1}/{len(addresses)}]: {address} => {lat}, {lon}")
        if lat is not None and lon is not None:
            coords.append((lon, lat))  # ORS requires (lon, lat)
        else:
            coords.append(None)
        time.sleep(1)
    return coords

def optimize_route_ors(coords, ors_api_key):
    try:
        client = openrouteservice.Client(key=ors_api_key)

        if len(coords) < 3:
            print("❌ Must have at least start, 1 stop, and end.")
            return None

        start = coords[0]
        end = coords[-1]
        jobs = [{"id": i+1, "location": loc} for i, loc in enumerate(coords[1:-1])]

        vehicle = {
            "id": 1,
            "start": start,
            "end": end,
        }

        print("🔧 Optimization Request:")
        print(f"Start: {start}")
        print(f"End: {end}")
        print(f"Jobs: {jobs}")

        result = client.optimization(jobs=jobs, vehicles=[vehicle])
        print("✅ Optimization Response Received")

        steps = result['routes'][0]['steps']
        job_order = {step['id']: step['location'] for step in steps}
        return job_order

    except openrouteservice.exceptions.ApiError as e:
        print("❌ ORS API Error:", e)
        return None
    except Exception as e:
        print("❌ Unexpected Error:", e)
        return None
