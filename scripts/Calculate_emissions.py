import pandas as pd


data=pd.read_excel("backend/data/Historic_travels/Déplacement-mode.xlsx",sheet_name="Feuil1",header=1)

emission_plane_data=pd.read_csv("backend/data/calculated_travels/flight_emissions.csv")
emission_train_data=pd.read_csv("backend/data/calculated_travels/train_emissions.csv")
emission_car_data=pd.read_csv("backend/data/calculated_travels/car_emissions.csv")


data_historic_travels=data.iloc[0:18]

reconstructed_data = pd.melt(
    data_historic_travels,
    id_vars=["v"],
    var_name="Host team",
    value_name="Transport"
)

reconstructed_data = reconstructed_data.rename(columns={"v": "Visiting team"})

def get_data(visiting_team, hosting_team,transport):
    if transport=="avion":
        dataset=emission_plane_data
    elif transport=="bus":
        dataset=emission_car_data
    elif transport=="train":
        dataset=emission_train_data
    else:
        return 0,0
    
    subset = dataset[
        (dataset["departure"] == visiting_team) &
        (dataset["arrival"] == hosting_team)
    ]
    
    if subset.empty:
        subset2= dataset[
        (dataset["departure"] == hosting_team) &
        (dataset["arrival"] == visiting_team)
        ]
        emission_in_kg = subset2["emissions_kg_co2"].iloc[0]
        time_in_sec = subset2["travel_time_seconds"].iloc[0]
    else:
        emission_in_kg = subset["emissions_kg_co2"].iloc[0]
        time_in_sec = subset["travel_time_seconds"].iloc[0]
    
    return emission_in_kg, time_in_sec


list_emissions=[]
list_time=[]
for i in range(len(reconstructed_data)):
    visiting_team = reconstructed_data.iloc[i, 0]
    hosting_team = reconstructed_data.iloc[i, 1]
    transport = reconstructed_data.iloc[i, 2]
    
    emission, time = get_data(visiting_team, hosting_team, transport)
    
    if transport!='bus' and visiting_team!=hosting_team:
        emission_bus,time_bus=get_data(visiting_team, hosting_team, "bus")
        emission+=emission_bus
    
    list_emissions.append(emission)
    list_time.append(time)



list_alternative_emissions=[]
list_alternative_time=[]
list_alternative_emissions_wo_bus=[]
for i in range(len(reconstructed_data)):
    visiting_team = reconstructed_data.iloc[i, 0]
    hosting_team = reconstructed_data.iloc[i, 1]

    if visiting_team!=hosting_team:
        emission_train, time_train = get_data(visiting_team, hosting_team, "train")
        emission_bus, time_bus = get_data(visiting_team, hosting_team, "bus")

        if time_bus<time_train:
            list_alternative_emissions.append(emission_bus)
            list_alternative_emissions_wo_bus.append(emission_bus)
            list_alternative_time.append(time_bus)
        else:
            emission_train_w_bus=emission_train+emission_bus
            list_alternative_emissions.append(emission_train_w_bus)
            list_alternative_emissions_wo_bus.append(emission_train)
            list_alternative_time.append(time_train)
    else:
        list_alternative_emissions.append(0)
        list_alternative_emissions_wo_bus.append(0)
        list_alternative_time.append(0)

final_df = reconstructed_data.copy()
final_df["emissions_kg_co2"] = list_emissions
final_df["travel_time_seconds"] = list_time
final_df["alternative_emissions_kg_co2"] = list_alternative_emissions
final_df["alternative_emissions_kg_co2_wo_empty_bus"] = list_alternative_emissions_wo_bus
final_df["alternative_travel_time_seconds"] = list_alternative_time

final_df.to_csv("backend/data/calculated_travels/total_emmissions.csv",index=False)