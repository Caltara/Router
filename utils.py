import openrouteservice
from geopy.geocoders import Nominatim
import time

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
    for address in addresses:
        lat, lon = geocode_address(address)
        if lat is not None and lon is not None:
            coords.append((lon, lat))  # ORS expects (lon, lat)
        else:
            coords.append(None)
        time.sleep(1)  # prevent rate limiting
    return coords

def optimize_route_ors(coords, ors_api_key):
    client = openrouteservice.Client(key=ors_api_key)

    try:
        optimized = client.optimization(
            jobs=[{"id": i+1, "location": loc} for i, loc in enumerate(coords[1:-1])],
            vehicles=[{
                "id": 1,
                "start": coords[0],
                "end": coords[-1],
            }]
        )
        job_order = {job['id']: job['location'] for job in optimized['routes'][0]['steps']}
        return job_order
    except Exception as e:
        print(f"ORS Optimization Error: {e}")
        return None
