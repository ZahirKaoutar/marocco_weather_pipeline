import pandas as pd
import requests
import json
import os
import datetime
import time
from pathlib import Path

def extraction():
    BASE_DIR = Path(__file__).resolve().parents[1]
    cities_file = BASE_DIR / "data" / "ma.csv"
    df_cities = pd.read_csv(cities_file)
    all_weather = []
    for _, ville in df_cities.iterrows():

        city = ville["city"]
        lat = ville["lat"]
        lng = ville["lng"]

        print(f"Récupération : {city}")
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lng,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "weather_code"
            ],
            "timezone": "Africa/Casablanca"
        }

        max_retries = 3
        retry_delay = 2
        success = False
        for attempt in range(max_retries):

            try:

                response = requests.get(
                    url,
                    params=params,
                    timeout=10
                )

                response.raise_for_status()

                data = response.json()

                if "daily" not in data:
                    raise ValueError(
                        "La clé 'daily' est absente de la réponse de l'API."
                    )
                df_weather = pd.DataFrame(data["daily"])
                df_weather["city"] = city
                df_weather["lat"] = lat
                df_weather["lng"] = lng
                all_weather.append(df_weather)

                success = True
                break

            except requests.exceptions.Timeout:

                print(
                    f"Timeout pour {city} "
                    f"(Tentative {attempt + 1}/{max_retries})"
                )

            except requests.exceptions.HTTPError as err_http:

                print(
                    f"Erreur HTTP pour {city} : {err_http} "
                    f"(Tentative {attempt + 1}/{max_retries})"
                )

            except requests.exceptions.RequestException as e:

                print(
                    f"Erreur de connexion pour {city} : {e} "
                    f"(Tentative {attempt + 1}/{max_retries})"
                )

            except ValueError as ve:

                print(
                    f"Données invalides pour {city} : {ve} "
                    f"(Tentative {attempt + 1}/{max_retries})"
                )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        if not success:

            print(
                f"Impossible de récupérer les données pour {city} "
                f"après {max_retries} tentatives. "
                f"On ignore cette ville."
            )

    if not all_weather:

        raise Exception(
            "Aucune donnée n'a pu être récupérée "
            "pour l'ensemble des villes."
        )

    df_final = pd.concat(
        all_weather,
        ignore_index=True
    )

    bronze_data = df_final.to_dict(
        orient="records"
    )
    
    bronz_dir = BASE_DIR / "data" / "bronze"

    os.makedirs(
        bronz_dir,
        exist_ok=True
    )
    today_date = datetime.datetime.now().strftime(
        "%Y-%m-%d"
    )
    
    output_path = bronz_dir / f"weather_raw_{today_date}.json" 

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            bronze_data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(
        "Fichier Bronze créé :",
        output_path
    )
if __name__=='main':
    extraction()