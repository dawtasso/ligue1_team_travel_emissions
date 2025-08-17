import requests
from math import radians, sin, cos, sqrt, acos
import pandas as pd
import sys

API_KEY=sys.argv[1]

def is_real_airport(place_name):
    keywords = ['airport', "Airport", "Aeroport", "Aéroport", 'aéroport', 'aeroport']
    return any(word.lower() in place_name.lower() for word in keywords)


def get_nearest_airport(lat, lon, api_key):
    import requests

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
        # Find the first valid airport
        valid_result = next(
            (place for place in data["results"] if is_real_airport(place["name"])),
            None
        )

        if valid_result:
            return {
                "name": valid_result["name"],
                "latitude": valid_result["geometry"]["location"]["lat"],
                "longitude": valid_result["geometry"]["location"]["lng"]
            }
        else:
            return {"error": "No real airport found in results"}
    else:
        return {"error": data.get("status", "No results")}


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = acos(1-2*a)

    distance_km = R * c
    return distance_km

loc_df=pd.read_csv("localisation_stade.csv",index_col=0)


l_name=[]
l_lat=[]
l_lon=[]

for i in loc_df.index:
    lat=loc_df.iloc[i,3]
    lon=loc_df.iloc[i,4]
    d=get_nearest_airport(lat,lon,API_KEY)
    air_name=d['name']
    air_lat=d['latitude']
    air_lon=d['longitude']
    l_name.append(air_name)
    l_lat.append(air_lat)
    l_lon.append(air_lon)

loc_df["nearest aiport"]=l_name
loc_df["Airport lat"]=l_lat
loc_df["Airport lon"]=l_lon

loc_df.to_csv("loc_airport.csv")