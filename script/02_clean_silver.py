import pandas as pd
import numpy as np
import os
import json

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

for colonne in val_nums:
    df_bronz[colonne] = pd.to_numeric(
        df_bronz[colonne],
        errors="coerce"
    )


df_bronz["time"] = pd.to_datetime(
    df_bronz["time"],
    errors="coerce"
)


print("Dates invalides :", df_bronz["time"].isna().sum())



df_bronz = df_bronz.dropna(subset=["time"])
df_bronz["month"]=df_bronz["time"].dt.month
df_bronz["year"]=df_bronz["time"].dt.year
df_bronz["day"]=df_bronz["time"].dt.day

f_gold = pd.read_json(
    "data/silver/silver_2026-09-14.json"
)
conditions = [
    df_bronz["temperature_2m_max"] < 10,
    df_bronz["temperature_2m_max"] < 20,
    df_bronz["temperature_2m_max"] < 30,
    df_bronz["temperature_2m_max"] < 35,
    df_bronz["temperature_2m_max"] >= 35
]

choices = [
    "Froide",
    "Fraîche",
    "Modérée",
    "Chaude",
    "Très chaude"
]
df_bronz["temperature_category"] = np.select(
    conditions,
    choices,
    default="Inconnue"
)

conditions = [
    df_bronz["precipitation_sum"] == 0,
    df_bronz["precipitation_sum"] <= 2.5,
    df_bronz["precipitation_sum"] <= 10,
    df_bronz["precipitation_sum"] > 10
]
choices = [
    "Aucune",
    "Faible",
    "Modérée",
    "Forte"
]
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
choices = [
    "Faible",
    "Modéré",
    "Fort",
    "Très fort"
]
df_bronz["wind_category"] = np.select(
    conditions,
    choices,
    default="Inconnue"
)




nombre_doublons = df_bronz.duplicated().sum()
number_val_nan=df_bronz.isna().sum()
print("nombre de valeur_null en data:",number_val_nan)

print("Nombre de doublons :", nombre_doublons)

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



# silver_data = df_silver.to_dict(
#     orient="records"
# )



# file_path_silver = "data/silver/silver_2026-09-14.json"

# with open(
#     file_path_silver,
#     "w",
#     encoding="utf-8"
# ) as f:

#     json.dump(
#         silver_data,
#         f,
#         ensure_ascii=False,
#         indent=4,
#         default=str
#     )


# print("Fichier Silver créé :", file_path_silver)







file_path_silver = "data/silver/silver_2026-09-14.csv"



df_silver.to_csv(
        file_path_silver,
       
       index=False
    )


print("Fichier Silver créé :", file_path_silver)


print(df_silver.head())