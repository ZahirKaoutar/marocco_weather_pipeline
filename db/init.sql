-- Initialize databases and users
SELECT 'CREATE DATABASE meteo_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'meteo_db')\gexec

DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'postgres') THEN

      CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';
   END IF;
END
$do$;

GRANT ALL PRIVILEGES ON DATABASE meteo_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE airflow TO postgres;

