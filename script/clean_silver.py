import os
import glob
from datetime import datetime
import pandas as pd
import numpy as np


def transformation():
    file_path1 = "data/ma.csv"
    today_date = datetime.now().strftime("%Y-%m-%d")
    file_path2 = f"data/bronze/weather_raw_{today_date}.json"

    # Vérifier l'existence du fichier bronze du jour ou prendre le plus récent
    if not os.path.exists(file_path2):
        bronze_files = sorted(glob.glob("data/bronze/weather_raw_*.json"))
        if bronze_files:
            file_path2 = bronze_files[-1]
            print(f"Fichier du jour non trouvé, utilisation du dernier fichier bronze : {file_path2}")
        else:
            raise FileNotFoundError(f"Aucun fichier bronze trouvé dans data/bronze/ (recherché : {file_path2})")
    else:
        print(f"Chargement du fichier bronze : {file_path2}")

    df_bronz = pd.read_json(file_path2)
    df_ma = pd.read_csv(file_path1)

    # Harmonisation des noms de colonnes provenant de l'API Open-Meteo
    rename_cols = {
        "wind_speed_10m_max": "windspeed_10m_max",
        "wind_gusts_10m_max": "windgusts_10m_max",
        "weather_code": "weathercode"
    }
    df_bronz = df_bronz.rename(columns=rename_cols)

    val_nums = [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "precipitation_probability_max",
        "windspeed_10m_max",
        "windgusts_10m_max",
        "weathercode"
    ]

    # Convertir en numérique
    for col in val_nums:
        if col in df_bronz.columns:
            df_bronz[col] = pd.to_numeric(df_bronz[col], errors="coerce")

    if "weathercode" in df_bronz.columns:
        df_bronz["weathercode"] = df_bronz["weathercode"].fillna(0)

    df_bronz = df_bronz.dropna(subset=["time", "city"])

    if "precipitation_sum" in df_bronz.columns:
        df_bronz["precipitation_sum"] = df_bronz["precipitation_sum"].fillna(0)
    if "windgusts_10m_max" in df_bronz.columns:
        df_bronz["windgusts_10m_max"] = df_bronz["windgusts_10m_max"].fillna(0)
    if "precipitation_probability_max" in df_bronz.columns:
        df_bronz["precipitation_probability_max"] = df_bronz["precipitation_probability_max"].fillna(0)

    df_bronz = df_bronz.sort_values(["city", "time"])

    val_miss = [col for col in [
        "temperature_2m_max", "temperature_2m_min",
        "windspeed_10m_max", "windgusts_10m_max"
    ] if col in df_bronz.columns]

    df_bronz[val_miss] = df_bronz.groupby("city")[val_miss].transform(lambda x: x.fillna(x.mean()))

    df_bronz["time"] = pd.to_datetime(df_bronz["time"], errors="coerce")
    df_bronz = df_bronz.dropna(subset=["time"])
    df_bronz["month"] = df_bronz["time"].dt.month
    df_bronz["year"] = df_bronz["time"].dt.year
    df_bronz["day"] = df_bronz["time"].dt.day

    # Catégories de température
    conditions_temp = [
        df_bronz["temperature_2m_max"] < 10,
        df_bronz["temperature_2m_max"] < 20,
        df_bronz["temperature_2m_max"] < 30,
        df_bronz["temperature_2m_max"] < 38,
        df_bronz["temperature_2m_max"] >= 38
    ]
    choices_temp = ["Froide", "Fraîche", "Modérée", "Chaude", "Extrême"]
    df_bronz["temperature_category"] = np.select(conditions_temp, choices_temp, default="Inconnue")

    # Catégories de précipitations
    conditions_precip = [
        df_bronz["precipitation_sum"] == 0,
        df_bronz["precipitation_sum"] <= 2.5,
        df_bronz["precipitation_sum"] <= 10,
        df_bronz["precipitation_sum"] <= 30,
        df_bronz["precipitation_sum"] > 30
    ]
    choices_precip = ["Aucune", "Faible", "Modérée", "Forte", "Très forte"]
    df_bronz["precipitation_category"] = np.select(conditions_precip, choices_precip, default="Inconnue")

    # Catégories de vent
    conditions_wind = [
        df_bronz["windspeed_10m_max"] < 20,
        df_bronz["windspeed_10m_max"] < 40,
        df_bronz["windspeed_10m_max"] < 60,
        df_bronz["windspeed_10m_max"] >= 60
    ]
    choices_wind = ["Faible", "Modéré", "Fort", "Très fort"]
    df_bronz["wind_category"] = np.select(conditions_wind, choices_wind, default="Inconnue")

    # Déduplication
    if df_bronz.duplicated().sum() != 0:
        df_bronz = df_bronz.drop_duplicates()

    # Fusion avec coordonnées si nécessaire
    if "lat" not in df_bronz.columns or "lng" not in df_bronz.columns:
        df_silver = df_bronz.merge(
            df_ma[["city", "lat", "lng"]],
            on="city",
            how="left"
        )
    else:
        df_silver = df_bronz

    os.makedirs("data/silver", exist_ok=True)

    file_path_silver = f"data/silver/silver_{today_date}.csv"
    df_silver.to_csv(file_path_silver, index=False)
    # Écrire aussi dans un fichier générique pour les scripts suivants
    df_silver.to_csv("data/silver/weather_silver.csv", index=False)

    print("Fichier Silver créé :", file_path_silver)
    print(df_silver.head())
    return df_silver


if __name__ == "__main__":
    transformation()