import pandas as pd


df_flight=pd.read_csv("flight_emissions.csv",index_col=0)

data_per_match=df_flight[['Hosting team', 'visiting team',"time plane (in seconds)", 'Total emission (aller-retour)']]
data_per_match.columns = ['Hosting team', 'visiting team',"Time", 'emission_carbone']

list_team=data_per_match["visiting team"].unique()

dict_team = {team: 0 for team in list_team}

for i in data_per_match.index:
    team=data_per_match.iloc[i,1]
    dict_team[team]+=data_per_match.iloc[i,3]

for team in dict_team:
    dict_team[team] *= 0.82

df_final = pd.DataFrame({
    "Equipe": list(dict_team.keys()),
    "Emissions carbone (kgCO2)": list(dict_team.values())
})

data_per_match.to_csv("emission_carbone_match.csv")
df_final.to_csv("emission_carbone_team.csv")