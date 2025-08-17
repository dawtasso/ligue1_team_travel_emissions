import pandas as pd
from math import radians, sin, cos, sqrt, acos
import requests
import sys


API_KEY=sys.argv[1]
#Source: https://bigmedia.bpifrance.fr/nos-dossiers/empreinte-carbone-des-trajets-en-train-calcul-et-decarbonation
Emission_autocar_perkm=30 #gCO2/passagers/km
percentage_of_fuel_in_total_plane_emission=141/260 #in %

#Source: https://www.iata.org/contentassets/922ebc4cbcd24c4d9fd55933e7070947/icop_faq_general-for-airline-participants.pdf
jet_fuel_to_CO2=3.16 #1 kg of jet fuel produces 1 kg of CO2
passengers=int(sys.argv[2])

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

def fuel_consumption(distance): #see excel
    a=1287.86079089524
    b=2.97350834930426
    return(a+b*distance)


def time_plane(distance):
    a=0.285387849787546
    b=0.00120352141554664
    time_in_100=a+b*distance
    hours=int(time_in_100)
    minutes=(time_in_100 - hours)*60
    seconds=hours*3600+minutes*60
    return(seconds)

def get_distance_duration(cor1, cor2):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": cor1,  
        "destination": cor2, 
        "mode": "driving",
        "alternatives": "false",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    try:
        leg = data["routes"][0]["legs"][0]
        distance_meters = leg["distance"]["value"]           # in meters
        duration_seconds = leg["duration"]["value"]          # in seconds
        return distance_meters, duration_seconds
    except (KeyError, IndexError):
        return None, None


loc_df=pd.read_csv("loc_airport.csv",index_col=0)
df=pd.DataFrame([])

l_name=[]
l_hosting=[]
l_visiting=[]
l_distance=[]
l_distance_autocar=[]
l_time_autocar=[]
l_fuel_consumption=[]
l_emission_autocar=[]
l_emission_plane=[]
l_time_plane=[]
l_total_time=[]
l_total_emission=[]

for i in loc_df.index:
    print(i)
    distance_autocar=0
    time_autocar=0
    hosting=loc_df.iloc[i,0]
    lat1=loc_df.iloc[i,6]
    lon1=loc_df.iloc[i,7]
    lat1_stade=loc_df.iloc[i,3]
    lon1_stade=loc_df.iloc[i,4]
    cor1=str(lat1_stade)+','+str(lon1_stade)
    cor2=str(lat1)+','+str(lon1)
    dis_i,time_i=get_distance_duration(cor1,cor2)
    distance_autocar+=dis_i/1000
    time_autocar+=time_i

    for j in loc_df.index:
        if i!=j:
            visiting=loc_df.iloc[j,0]
            name=hosting+";-"+visiting

            lat2=loc_df.iloc[j,6]
            lon2=loc_df.iloc[j,7]
            distance=haversine(lat1,lon1,lat2,lon2)
            f_c=fuel_consumption(distance)
            emission_plane=jet_fuel_to_CO2*f_c/percentage_of_fuel_in_total_plane_emission
            time_plane_value=time_plane(distance)


            lat2_stade=loc_df.iloc[j,3]
            lon2_stade=loc_df.iloc[j,4]
            cor4=str(lat2_stade)+','+str(lon2_stade)
            cor3=str(lat2)+','+str(lon2)
            dis_j,time_j=get_distance_duration(cor3,cor4)
            distance_autocar+=dis_j/1000
            time_autocar+=time_j
            time_total=time_autocar+time_plane_value

            Emission_autocar=Emission_autocar_perkm*distance_autocar

            total_emission=Emission_autocar+emission_plane

            
            l_name+=[name]
            l_hosting+=[hosting]
            l_visiting+=[visiting]
            l_distance+=[distance] #in km
            l_fuel_consumption+=[f_c] #in kg
            l_distance_autocar+=[distance_autocar]#in km
            l_time_autocar+=[time_autocar]# in sec
            l_emission_autocar+=[Emission_autocar*50/1000] #in kg
            l_emission_plane+=[emission_plane]
            l_total_emission+=[total_emission*2]
            l_time_plane+=[time_plane_value]#seconds
            l_total_time+=[time_total]
            

            distance_autocar=dis_i/1000
            time_autocar=time_i




df["name"]=l_name
df["Hosting team"]=l_hosting
df["visiting team"]=l_visiting
df["distance (in km)"]=l_distance
df["time plane (in seconds)"]=l_time_plane
df["fuel consumption (in kg)"]=l_fuel_consumption
df["Emission plane (in kg)"]=l_emission_plane
df["distance autocar (in km)"]=l_distance_autocar
df["time autocar (in sec)"]=l_time_autocar
df["Emission autocar (in kg)"]=l_emission_autocar
df["Total time (in seconds)"]=l_total_time
df["Total emission (aller-retour)"]=l_total_emission


print(df)

df.to_csv("flight_emissions.csv")