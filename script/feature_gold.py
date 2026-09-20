import os
import glob
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

def create_gold():
    BASE_DIR = Path(__file__).resolve().parents[1]
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    file_path = BASE_DIR / f"data/silver/silver_{today_date}.csv"

    if not file_path.exists():
        fallback = BASE_DIR / "data/silver/weather_silver.csv"
        if fallback.exists():
            file_path = fallback
            print(f"Fichier silver du jour non trouvé, utilisation de : {file_path}")
        else:
            silver_files = sorted(glob.glob(str(BASE_DIR / "data/silver/silver_*.csv")))
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

 
    df_gold["score_code_weather"] = df_gold["weathercode"].apply(weather_to_score)

    # =====================================================================
    # JUSTIFICATION DU WEATHER RISK SCORE (Pour l'entreprise de livraison)
    # =====================================================================
    # Variables utilisées : 
    #   - Température moyenne : Risque pour le livreur (insolation ou verglas) et le véhicule.
    #   - Précipitations : Risque d'inondations, visibilité réduite et routes glissantes.
    #   - Vent et Rafales : Risque de déviation des véhicules (deux-roues ou camions légers).
    #   - Code Météo (WMO) : Indicateur global (orages, neige) aggravant les conditions.
    # 
    # Seuils choisis (normalisation de 0 à 100) :
    #   - Température : Pénalité si > 30°C (risque chaleur) ou < 10°C (risque froid). 
    #   - Pluie : Le risque devient maximal (100) à partir de 40 mm/jour (fortes précipitations au Maroc).
    #   - Vent max : Risque maximal à 80 km/h (seuil critique de conduite).
    #   - Rafales : Risque maximal à 100 km/h (danger imminent pour les livreurs).
    #
    # Méthode de calcul (Pondération totale = 1.00) :
    #   La pluie est le facteur le plus bloquant pour les livraisons (35%).
    #   Le vent et les rafales sont séparés (20% + 20% = 40%) pour pénaliser les pics de danger.
    #   La température (15%) et le code météo global (10%) ajustent le score final.
    # =====================================================================
    
    df_gold["weather_risk_score"] = (
        df_gold["score_temperature"] * 0.15
        + df_gold["score_pluie"] * 0.35
        + df_gold["score_vent"] * 0.20
        + df_gold["score_rafales"] * 0.20
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



    os.makedirs(BASE_DIR / "data/gold", exist_ok=True)
    gold_path = BASE_DIR / "data/gold/weather_gold.csv"
    gold.to_csv(gold_path, index=False)
    print(f"\nFichier Gold créé avec succès : {gold_path}")
    return gold


if __name__=='main':

    create_gold()