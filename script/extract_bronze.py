# import pandas as pd
# import datetime
# import json
# import os

# file_path = "api/weather_data_2026-09-14.csv"

# df_weather = pd.read_csv(file_path)

# bronze_data = df_weather.to_dict(orient="records")


# os.makedirs("data/bronze", exist_ok=True)

# #
# today_date = datetime.datetime.now().strftime("%Y-%m-%d")


# output_path = f"data/bronze/weather_raw_{today_date}.json"

# with open(output_path, "w", encoding="utf-8") as file:
#     json.dump(
#         bronze_data,
#         file,
#         ensure_ascii=False,
#         indent=4
#     )

# print("Fichier Bronze créé :", output_path)






import pandas as pd
import requests
import json
import os
import datetime


def extraction():
# Lire le fichier des villes
    df_cities = pd.read_csv("data/ma.csv")

    all_weather = []


    # Boucle sur les villes
    for index, ville in df_cities.iterrows():

        city = ville["city"]
        lat = ville["lat"]
        lng = ville["lng"]

        print("Récupération :", city)

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

        response = requests.get(url, params=params)

        data = response.json()

        # Transformer les données météo en DataFrame
        df_weather = pd.DataFrame(data["daily"])

        # Ajouter les informations de la ville
        df_weather["city"] = city
        df_weather["lat"] = lat
        df_weather["lng"] = lng

        # Ajouter à la liste
        all_weather.append(df_weather)


    # Regrouper toutes les villes
    df_final = pd.concat(all_weather, ignore_index=True)


    # Transformer en liste de dictionnaires
    bronze_data = df_final.to_dict(orient="records")


    # Créer le dossier Bronze
    os.makedirs("data/bronze", exist_ok=True)


    # Date
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")


    # Fichier de sortie
    output_path = f"data/bronze/weather_raw_{today_date}.json"


    # Sauvegarder
    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(
            bronze_data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("Fichier Bronze créé :", output_path)

    print("Fichier Bronze créé :", output_path)

if __name__ == "__main__":
    extraction()