import pandas as pd
import numpy as np
import os


file_path1 = "data/ma.csv"
file_path2 = "data/bronze/weather_raw_2026-09-14.json"


df_bronz = pd.read_json(file_path2)
df_ma = pd.read_csv(file_path1)
val_nums = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "windspeed_10m_max",
    "windgusts_10m_max",
    "weathercode"
]

df_bronz[val_nums] = df_bronz[val_nums].apply(pd.to_numeric, errors="coerce")
df_bronz["weathercode"] = df_bronz["weathercode"].fillna(0)
df_bronz=df_bronz.dropna(subset=["time","cities"])
df_bronz["precipitation_sum"]=df_bronz["precipitation_sum"].fillna(0)
df_bronz["windgusts_10m_max"]=df_bronz["windgusts_10m_max"].fillna(0)
df_bronz["precipitation_probability_max"]=df_bronz["precipitation_probability_max"].fillna(0)
df_bronz=df_bronz.sort_values(["cities","time"])
val_miss= [
    "temperature_2m_max", "temperature_2m_min",
    "windspeed_10m_max", "windgusts_10m_max"
]
df_bronz[val_miss]=df_bronz.groupby("cities")[val_miss].transform(lambda x:x.fillna(x.mean()))






df_bronz["time"] = pd.to_datetime(
    df_bronz["time"],
    errors="coerce"
)





df_bronz = df_bronz.dropna(subset=["time"])
df_bronz["month"]=df_bronz["time"].dt.month
df_bronz["year"]=df_bronz["time"].dt.year
df_bronz["day"]=df_bronz["time"].dt.day


conditions = [
    df_bronz["temperature_2m_max"] < 10,   
    df_bronz["temperature_2m_max"] < 20,   
    df_bronz["temperature_2m_max"] < 30,  
    df_bronz["temperature_2m_max"] < 38,   
    df_bronz["temperature_2m_max"] >= 38  
]
choices = ["Froide", "Fraîche", "Modérée", "Chaude", "Extrême"]

df_bronz["temperature_category"] = np.select(
    conditions,
    choices,
    default="Inconnue"
)


conditions = [
    df_bronz["precipitation_sum"] == 0,
    df_bronz["precipitation_sum"] <= 2.5,
    df_bronz["precipitation_sum"] <= 10,
    df_bronz["precipitation_sum"] <= 30,
    df_bronz["precipitation_sum"] > 30
]
choices = ["Aucune", "Faible", "Modérée", "Forte", "Très forte"]

df_bronz["precipitation_category"] = np.select(
    conditions,
    choices,
    default="Inconnue"
)

conditions = [
    df_bronz["windspeed_10m_max"] < 20,
    df_bronz["windspeed_10m_max"] < 40,
    df_bronz["windspeed_10m_max"] < 60,
    df_bronz["windspeed_10m_max"] >= 60
]
choices = ["Faible", "Modéré", "Fort", "Très fort"]

df_bronz["wind_category"] = np.select(
    conditions,
    choices,
    default="Inconnue"
)




nombre_doublons = df_bronz.duplicated().sum()
number_val_nan=df_bronz.isna().sum()

if nombre_doublons != 0:
    df_bronz = df_bronz.drop_duplicates()

df_bronz = df_bronz.rename(
    columns={"cities": "city"}
)


df_silver = df_bronz.merge(
    df_ma[["city", "lat", "lng"]],
    on="city",
    how="left"
)





os.makedirs("data/silver", exist_ok=True)







file_path_silver = "data/silver/silver_2026-09-14.csv"
df_silver.to_csv(file_path_silver,index=False)
print("Fichier Silver créé :", file_path_silver)


print(df_silver.head())