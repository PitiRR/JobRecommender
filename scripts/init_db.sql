CREATE DATABASE airflow_db;
-- CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow;
-- PostgreSQL 15 requires additional privileges:
\c airflow_db;
GRANT ALL ON SCHEMA public TO airflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO airflow;

CREATE DATABASE jobs_db;
GRANT ALL PRIVILEGES ON DATABASE jobs_db TO airflow;

-- PostgreSQL 15 requires additional privileges:
\c jobs_db;
GRANT ALL ON SCHEMA public TO airflow;

CREATE TABLE IF NOT EXISTS jobs (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Core
    title TEXT,
    company TEXT,
    location TEXT,
    url TEXT UNIQUE NOT NULL, -- Natural key, always unique in practice
    description TEXT,
    added_date DATE,

    -- Salary
    sal_min NUMERIC,
    sal_max NUMERIC,

    -- Categorical
    level TEXT[],
    schedule TEXT[],
    mode TEXT[],
    contract TEXT[],
    skills TEXT[],
    requirements TEXT[],
    responsibilities TEXT[],
    benefits TEXT[],

    -- ML/Ranking score
    score FLOAT
);

CREATE INDEX idx_jobs_url ON jobs (url);
CREATE INDEX idx_jobs_added_date ON jobs (added_date);
