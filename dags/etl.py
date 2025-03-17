import logging
import os
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

from dotenv import load_dotenv
from src.etl.extract import extract_from_jsearch, extract_from_pracuj
from src.etl.transform import clean_data
from src.utils.config import start_logger


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 16),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

logger = logging.getLogger(__name__)
load_dotenv()
airflow_email = os.getenv('AIRFLOW_EMAIL')

@dag(
    start_date=datetime(2025, 2, 16),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
)
def get_jobs_etl(email = airflow_email):
    """Scrape job postings from jsearch and pracuj.pl, clean the data and load it to the database"""
    dag_id = 'get_jobs_etl'
    logging.info("Start task initiated")
    start_logger()

    database_url = 'postgresql://airflow:airflow@postgres:5432/airflow_metadata'
    engine = create_engine(database_url)

    start_task = EmptyOperator(task_id='start_task')

    @task(task_id='extract_task')
    def extract_jobs():
        jsearch_results = extract_from_jsearch()
        logger.info("Finished extracting jsearch_results")
        pracujpl_results = extract_from_pracuj()
        logger.info("Finished extracting extract_from_pracuj")

        data = [job.__dict__ for job in jsearch_results + pracujpl_results]
        df = pd.DataFrame(data)
        return df

    @task(task_id='transform_task')
    def transform_jobs(df):
        """Transform and clean the dataframe"""
        df = clean_data(df)
        return df

    @task(task_id='load_task')
    def load_to_db(df):
        df.to_sql('job_postings', engine, if_exists='replace', index=False)
        logging.info("DataFrame deployed to job_postings table in the database.")

    end_task = EmptyOperator(task_id='end_task')

    df_extracted = extract_jobs()
    df_transformed = transform_jobs(df_extracted)
    load_result = load_to_db(df_transformed)

    start_task >> df_extracted # type: ignore
    load_result >> end_task # type: ignore

get_jobs_etl = get_jobs_etl()
