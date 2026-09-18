from sqlalchemy import text
from db.connection import engine


def create_tables():
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS cities (
                id SERIAL PRIMARY KEY,
                city VARCHAR(100) NOT NULL UNIQUE,
                lat DOUBLE PRECISION NOT NULL,
                lng DOUBLE PRECISION NOT NULL
            );
        """))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS weather (
                id SERIAL PRIMARY KEY,
                city_id INTEGER NOT NULL,
                time TIMESTAMP NOT NULL,
                day INTEGER,
                month INTEGER,
                year INTEGER,
                temperature_2m_max DOUBLE PRECISION,
                temperature_2m_min DOUBLE PRECISION,
                temperature_moyenne_jour DOUBLE PRECISION,
                temperature_category VARCHAR(20),
                precipitation_sum DOUBLE PRECISION,
                precipitation_category VARCHAR(20),
                windspeed_10m_max DOUBLE PRECISION,
                windgusts_10m_max DOUBLE PRECISION,
                wind_category VARCHAR(20),
                weather_risk_score DOUBLE PRECISION,
                risk_category VARCHAR(20),

                CONSTRAINT fk_weather_city
                    FOREIGN KEY (city_id)
                    REFERENCES cities(id),

                CONSTRAINT unique_city_time
                    UNIQUE (city_id, time)
            );
        """))
    print("Tables vérifiées / créées avec succès !")


if __name__ == "__main__":
    create_tables()