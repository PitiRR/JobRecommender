CREATE DATABASE airflow_db;
CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow;
-- PostgreSQL 15 requires additional privileges:
\c airflow_db;
GRANT ALL ON SCHEMA public TO airflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO airflow;

CREATE DATABASE jobs_db;
CREATE USER jobs_user WITH PASSWORD 'jobs_pass';
GRANT ALL PRIVILEGES ON DATABASE jobs_db TO jobs_user;

-- PostgreSQL 15 requires additional privileges:
\c jobs_db;
GRANT ALL ON SCHEMA public TO jobs_user;

CREATE TABLE IF NOT EXISTS jobs (
    --- Core
    job_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    posted_at TIMESTAMP,
    --- Ranges
    salary NUMRANGE,
    --- Text/categories
    url VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    level text ARRAY[3],    -- junior, mid, senior
    schedule text ARRAY[2], -- full-time, part-time
    mode text ARRAY[4],    -- remote, hybrid, on-site, mobile
    contract text ARRAY[3], -- permanent, b2b, contract
    skills TEXT[],
    requirements TEXT[],
    responsibilities TEXT[],
    benefits TEXT[],
    --- ML/ranking
    score FLOAT
);
CREATE INDEX idx_title ON jobs (title);
CREATE INDEX idx_score ON jobs (score);