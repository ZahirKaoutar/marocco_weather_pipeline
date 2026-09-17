import pandas as pd
from sqlalchemy import text
from connection import engine


def get_top_temperatures():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT c.city, MAX(w.temperature_2m_max) as temp_max
            FROM cities c
            INNER JOIN weather w ON c.id = w.city_id
            GROUP BY c.city
            ORDER BY temp_max DESC
            LIMIT 10
        """), conn)


def get_top_precipitations():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT c.city, MAX(w.precipitation_sum) as precipitation_max
            FROM cities c
            INNER JOIN weather w ON c.id = w.city_id
            GROUP BY c.city
            ORDER BY precipitation_max DESC
            LIMIT 10
        """), conn)


def get_top_risque_moyen():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT c.city, ROUND(AVG(w.weather_risk_score)::numeric, 2) as risque_moyen
            FROM cities c
            INNER JOIN weather w ON c.id = w.city_id
            GROUP BY c.city
            ORDER BY risque_moyen DESC
            LIMIT 10
        """), conn)


def get_periodes_risque_max():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT w.time, MAX(w.weather_risk_score) as risque_max
            FROM weather w
            GROUP BY w.time
            ORDER BY risque_max DESC
            LIMIT 10
        """), conn)


def get_risque_par_ville():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT c.city, w.time, MAX(w.weather_risk_score) as risque_max
            FROM cities c
            INNER JOIN weather w ON c.id = w.city_id
            GROUP BY c.city, w.time
            ORDER BY c.city, risque_max DESC
        """), conn)
