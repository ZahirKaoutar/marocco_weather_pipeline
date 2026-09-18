import os
import glob
from datetime import datetime
import pandas as pd
import numpy as np


def create_gold():
    today_date = datetime.now().strftime("%Y-%m-%d")
    file_path = f"data/silver/silver_{today_date}.csv"

    if not os.path.exists(file_path):
        fallback = "data/silver/weather_silver.csv"
        if os.path.exists(fallback):
            file_path = fallback
            print(f"Fichier silver du jour non trouvé, utilisation de : {file_path}")
        else:
            silver_files = sorted(glob.glob("data/silver/silver_*.csv"))
            if silver_files:
                file_path = silver_files[-1]
                print(f"Utilisation du dernier fichier silver : {file_path}")
            else:
                raise FileNotFoundError("Aucun fichier silver trouvé dans data/silver/")
    else:
        print(f"Chargement du fichier silver : {file_path}")

    df_gold = pd.read_csv(file_path)

    df_gold["temperature_moyenne_jour"] = (
        df_gold["temperature_2m_max"]
        + df_gold["temperature_2m_min"]
    ) / 2

    score_chaleur = np.clip(
        (df_gold["temperature_moyenne_jour"] - 30) / 10 * 100,
        0,
        100
    )

    score_froid = np.clip(
        (10 - df_gold["temperature_moyenne_jour"]) / 10 * 100,
        0,
        100
    )

    df_gold["score_temperature"] = np.maximum(
        score_chaleur,
        score_froid
    )

    df_gold["score_pluie"] = np.clip(
        df_gold["precipitation_sum"] / 40 * 100,
        0,
        100
    )

    df_gold["score_vent"] = np.clip(
        df_gold["windspeed_10m_max"] / 80 * 100,
        0,
        100
    )

    df_gold["score_rafales"] = np.clip(
        df_gold["windgusts_10m_max"] / 100 * 100,
        0,
        100
    )

    def weather_to_score(code):
        if code in [0, 1]:                          return 0
        elif code in [2, 3]:                        return 10
        elif code in [45, 48]:                      return 30
        elif code in [51, 53, 55, 56, 57]:          return 50
        elif code in [61, 63, 65, 66, 67]:          return 60
        elif code in [71, 73, 75, 77]:              return 70
        elif code in [80, 81, 82]:                  return 80
        elif code in [85, 86]:                      return 85
        elif code in [95, 96, 99]:                  return 100
        else:                                       return 0

    weathercode_col = "weathercode" if "weathercode" in df_gold.columns else "weather_code"
    df_gold["score_code_weather"] = df_gold[weathercode_col].apply(weather_to_score)

    df_gold["weather_risk_score"] = (
        df_gold["score_temperature"] * 0.15
        + df_gold["score_pluie"] * 0.30
        + df_gold["score_vent"] * 0.25
        + df_gold["score_rafales"] * 0.30
        + df_gold["score_code_weather"] * 0.10
    )

    df_gold["risk_category"] = pd.cut(
        df_gold["weather_risk_score"],
        bins=[-1, 30, 60, 100],
        labels=["Faible", "Modéré", "Élevé"],
        include_lowest=True
    )

    df_gold["weather_risk_score"] = df_gold["weather_risk_score"].round(2)

    gold = df_gold[
        [
            "city",
            "time",
            "day",
            "month",
            "year",
            "lng",
            "lat",
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_moyenne_jour",
            "temperature_category",
            "precipitation_category",
            "wind_category",
            "precipitation_sum",
            "windspeed_10m_max",
            "windgusts_10m_max",
            "weather_risk_score",
            "risk_category"
        ]
    ]

    print("\n========== GOLD ==========\n")
    print(gold.head())

    os.makedirs("data/gold", exist_ok=True)
    gold_path = "data/gold/weather_gold.csv"
    gold.to_csv(gold_path, index=False)
    print(f"\nFichier Gold créé avec succès : {gold_path}")
    return gold


if __name__ == "__main__":
    create_gold()