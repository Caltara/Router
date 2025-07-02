import openrouteservice

def optimize_route_ors(coords, ors_api_key):
    """
    Optimize a route using OpenRouteService.

    Parameters:
        coords (list): List of (longitude, latitude) tuples.
        ors_api_key (str): Your ORS API key from secrets.

    Returns:
        dict: Ordered steps {job_id: location} or None on failure.
    """
    client = openrouteservice.Client(key=ors_api_key)

    if len(coords) < 3:
        print("❌ At least 3 coordinates required (start, 1 stop, end).")
        return None

    start = coords[0]
    end = coords[-1]

    # Create intermediate jobs (exclude start and end)
    jobs = [{"id": i+1, "location": loc} for i, loc in enumerate(coords[1:-1])]

    if not jobs:
        print("❌ No intermediate stops (jobs) found.")
        return None

    vehicle = {
        "id": 1,
        "start": start,
        "end": end,
    }

    try:
        print("🔧 Sending optimization request to ORS...")
        print("Start:", start)
        print("End:", end)
        print("Jobs:", jobs)

        result = client.optimization(jobs=jobs, vehicles=[vehicle])

        steps = result["routes"][0]["steps"]
        job_order = {step["id"]: step["location"] for step in steps}

        print("✅ Optimization successful!")
        return job_order

    except openrouteservice.exceptions.ApiError as e:
        print("❌ ORS API Error:", e)
        return None
    except Exception as e:
        print("❌ Unexpected error:", e)
        return None
