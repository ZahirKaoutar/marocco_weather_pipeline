import pandas as pd
import datetime
import json
import os

file_path = "api/weather_data_2026-09-14.csv"

df_weather = pd.read_csv(file_path)

bronze_data = df_weather.to_dict(orient="records")


os.makedirs("data/bronze", exist_ok=True)

#
today_date = datetime.datetime.now().strftime("%Y-%m-%d")


output_path = f"data/bronze/weather_raw_{today_date}.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(
        bronze_data,
        file,
        ensure_ascii=False,
        indent=4
    )

print("Fichier Bronze créé :", output_path)