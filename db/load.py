import os
import pandas as pd
from sqlalchemy import text
from datetime import datetime
from db.connection import engine
from db.tables import create_tables


def load_postgres():
    # S'assurer que les tables existent avant l'insertion
    create_tables()

    gold_path = "data/gold/weather_gold.csv"
    if not os.path.exists(gold_path):
        raise FileNotFoundError(f"Fichier introuvable : {gold_path}")

    df = pd.read_csv(gold_path)
    df["time"] = pd.to_datetime(df["time"])

    cities = df[["city", "lat", "lng"]].drop_duplicates(subset="city")

    with engine.begin() as conn:
        for _, row in cities.iterrows():
            conn.execute(text("""
                INSERT INTO cities (city, lat, lng)
                VALUES (:city, :lat, :lng)
                ON CONFLICT (city) DO NOTHING
            """), {"city": row["city"], "lat": float(row["lat"]), "lng": float(row["lng"])})

        for _, row in df.iterrows():
            city_id = conn.execute(
                text("SELECT id FROM cities WHERE city = :city"),
                {"city": row["city"]}
            ).scalar()

            conn.execute(
                text("""
                    INSERT INTO weather (city_id, time, day, month, year,
                        temperature_2m_max, temperature_2m_min, temperature_moyenne_jour,
                        temperature_category, precipitation_sum, precipitation_category,
                        windspeed_10m_max, windgusts_10m_max, wind_category,
                        weather_risk_score, risk_category)
                    VALUES (:city_id, :time, :day, :month, :year,
                        :temperature_2m_max, :temperature_2m_min, :temperature_moyenne_jour,
                        :temperature_category, :precipitation_sum, :precipitation_category,
                        :windspeed_10m_max, :windgusts_10m_max, :wind_category,
                        :weather_risk_score, :risk_category)
                    ON CONFLICT (city_id, time) DO UPDATE SET
                        weather_risk_score = EXCLUDED.weather_risk_score,
                        risk_category = EXCLUDED.risk_category
                """),
                {
                    "city_id": int(city_id),
                    "time": row["time"],
                    "day": int(row["day"]),
                    "month": int(row["month"]),
                    "year": int(row["year"]),
                    "temperature_2m_max": float(row["temperature_2m_max"]),
                    "temperature_2m_min": float(row["temperature_2m_min"]),
                    "temperature_moyenne_jour": float(row["temperature_moyenne_jour"]),
                    "temperature_category": str(row["temperature_category"]),
                    "precipitation_sum": float(row["precipitation_sum"]),
                    "precipitation_category": str(row["precipitation_category"]),
                    "windspeed_10m_max": float(row["windspeed_10m_max"]),
                    "windgusts_10m_max": float(row["windgusts_10m_max"]),
                    "wind_category": str(row["wind_category"]),
                    "weather_risk_score": float(row["weather_risk_score"]),
                    "risk_category": str(row["risk_category"])
                }
            )

    print(f"Chargement terminé avec succès ! {len(df)} enregistrements traités.")


if __name__ == "__main__":
    load_postgres()