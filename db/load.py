import pandas as pd
from sqlalchemy import text
from connection import engine
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
df = pd.read_csv(f"data/gold/weather_gold.csv")
df["time"] = pd.to_datetime(df["time"])

cities = df[["city", "lat", "lng"]].drop_duplicates(subset="city")

with engine.begin() as conn:
    for _, row in cities.iterrows():
        conn.execute(text("""
            INSERT INTO cities (city, lat, lng)
            VALUES (:city, :lat, :lng)
            ON CONFLICT (city) DO NOTHING
        """), {"city": row["city"], "lat": row["lat"], "lng": row["lng"]})
    for _,row in df.iterrows():
            city_id = conn.execute(
            text("SELECT id FROM cities WHERE city = :city"),
            {"city": row["city"]}
                ).scalar()

            conn.execute(text(""" ISERT INTO weather (city_id, time, day, month, year,
            temperature_2m_max, temperature_2m_min, temperature_moyenne_jour,
            temperature_category, precipitation_sum, precipitation_category,
            windspeed_10m_max, windgusts_10m_max, wind_category,
            weather_risk_score, risk_category)
            VALUES( :city_id, :time, :day, :month, :year,
            :temperature_2m_max, :temperature_2m_min, :temperature_moyenne_jour,
            :temperature_category, :precipitation_sum, :precipitation_category,
            :windspeed_10m_max, :windgusts_10m_max, :wind_category,
            :weather_risk_score, :risk_category)
            ON CONFLICT (city_id, time) DO UPDATE SET
            weather_risk_score = EXCLUDED.weather_risk_score,
            risk_category = EXCLUDED.risk_category""")
            ,
                {
        "city_id": city_id,
        "time": row["time"],
        "day": row["day"],
        "month": row["month"],
        "year": row["year"],
        "temperature_2m_max": row["temperature_2m_max"],
        "temperature_2m_min": row["temperature_2m_min"],
        "temperature_moyenne_jour": row["temperature_moyenne_jour"],
        "temperature_category": row["temperature_category"],
        "precipitation_sum": row["precipitation_sum"],
        "precipitation_category": row["precipitation_category"],
        "windspeed_10m_max": row["windspeed_10m_max"],
        "windgusts_10m_max": row["windgusts_10m_max"],
        "wind_category": row["wind_category"],
        "weather_risk_score": row["weather_risk_score"],
        "risk_category": str(row["risk_category"])
    })      
   
   