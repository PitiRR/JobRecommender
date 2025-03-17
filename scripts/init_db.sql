CREATE DATABASE airflow_db;
CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow;
-- PostgreSQL 15 requires additional privileges:
\c airflow_db;
GRANT ALL ON SCHEMA public TO airflow;

CREATE DATABASE jobs_db;
CREATE USER jobs_user WITH PASSWORD 'jobs_pass';
GRANT ALL PRIVILEGES ON DATABASE jobs_db TO jobs_user;

-- PostgreSQL 15 requires additional privileges:
\c jobs_db;
GRANT ALL ON SCHEMA public TO jobs_user;