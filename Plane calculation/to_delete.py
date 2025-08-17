import requests
from math import radians, sin, cos, sqrt, acos
import pandas as pd

API_KEY='AIzaSyDIf4jaKso1v7WmOVfUyZCLBVYmcOJnuH4'

def get_nearest_airport(lat, lon, api_key):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "location": f"{lat},{lon}",
        "radius": 50000, 
        "type": "airport",
        "key": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "OK" and data.get("results"):
        print(data)
        nearest = data["results"][0]
        name = nearest["name"]
        lat = nearest["geometry"]["location"]["lat"]
        lon = nearest["geometry"]["location"]["lng"]
        return {
            "name": name,
            "latitude": lat,
            "longitude": lon
        }
    else:
        return {"error": data.get("status", "No results")}


print(get_nearest_airport("47.786582", "3.588717",API_KEY))