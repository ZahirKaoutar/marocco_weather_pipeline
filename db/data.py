import pandas as pd
from sqlalchemy import text
from db.connection import engine


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
            SELECT TO_CHAR(w.time, 'YYYY-MM-DD') as time,
                   MAX(w.weather_risk_score) as risque_max
            FROM weather w
            GROUP BY w.time
            ORDER BY w.time ASC
        """), conn)


def get_risque_par_ville():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT c.city,
                   TO_CHAR(w.time, 'YYYY-MM-DD') as time,
                   MAX(w.weather_risk_score) as risque_max
            FROM cities c
            INNER JOIN weather w ON c.id = w.city_id
            GROUP BY c.city, w.time
            ORDER BY c.city, w.time ASC
        """), conn)


def get_number_ville():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT count(city) as number_city FROM cities
        """), conn)


def get_maximal_precipitation():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT max(precipitation_sum) as max_precipitation FROM weather
        """), conn)


def get_maximal_temp():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT max(temperature_2m_max) as max_temp FROM weather
        """), conn)


def get_all_villes():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT city FROM cities ORDER BY city
        """), conn)["city"].tolist()


def get_all_dates():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT DISTINCT TO_CHAR(time, 'YYYY-MM-DD') as date
            FROM weather ORDER BY date
        """), conn)["date"].tolist()


def get_categories_risque_aujourdhui():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT w.risk_category, COUNT(DISTINCT c.city) AS nombre_villes
            FROM weather w inner join cities c on c.id=w.city_id
            WHERE w.time = CURRENT_DATE
            GROUP BY w.risk_category
            ORDER BY nombre_villes DESC
        """), conn)


def get_categories_temperature_aujourdhui():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT w.temperature_category, COUNT(DISTINCT c.city) AS nombre_villes
             FROM weather w inner join cities c on c.id=w.city_id
            WHERE w.time = CURRENT_DATE
            GROUP BY w.temperature_category
            ORDER BY nombre_villes DESC
        """), conn)


def get_categories_precipitation_aujourdhui():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT w.precipitation_category, COUNT(DISTINCT c.city) AS nombre_villes
            FROM weather w inner join cities c on  c.id=w.city_id
            WHERE w.time = CURRENT_DATE
            GROUP BY w.precipitation_category
            ORDER BY nombre_villes DESC
        """), conn)


def get_categories_vent_aujourdhui():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT w.wind_category, COUNT(DISTINCT c.city) AS nombre_villes
             FROM weather w inner join cities c on c.id=w.city_id
            WHERE w.time = CURRENT_DATE
            GROUP BY w.wind_category
            ORDER BY nombre_villes DESC
        """), conn)

