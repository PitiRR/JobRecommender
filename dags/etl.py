import logging
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from sqlalchemy import create_engine
from psycopg2.extensions import register_adapter, AsIs

from dotenv import load_dotenv
from src.etl.extract import extract_from_jsearch, extract_from_pracuj
from src.etl.load import load_to_db
from src.etl.transform import clean_data

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 16),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

load_dotenv()
airflow_email = os.getenv('AIRFLOW_EMAIL')


# psycopg2 can't handle np arrays by default
# def adapt_numpy_array(numpy_array):
#     return list(numpy_array)

# register_adapter(np.ndarray, adapt_numpy_array)


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

    start_task = EmptyOperator(task_id='start_task')

    @task(task_id='extract_task')
    def extract_jobs():
        jsearch_results = extract_from_jsearch()
        logger.info("Finished extracting jsearch_results")
        pracujpl_results = extract_from_pracuj()
        logger.info("Finished extracting extract_from_pracuj")
        print(pracujpl_results)
        data = [job.__dict__ for job in jsearch_results + pracujpl_results]
        df = pd.DataFrame(data)  
        relevant_columns = ['requirements', 'responsibilities', 'level', 'schedule', 'mode', 'contract', 'benefits']
        with pd.option_context('display.max_columns', None,
                            'display.max_rows', None,
                            'display.max_colwidth', None):
            logger.info("Sample data BEFORE cleaning (relevant columns):\n%s", df[relevant_columns].head())
            logger.info("Null counts BEFORE cleaning (relevant columns):\n%s", df[relevant_columns].isnull().sum())
            logger.info("Sample data AFTER cleaning (relevant columns):\n%s", df[relevant_columns].head())
            logger.info("Null counts AFTER cleaning (relevant columns):\n%s", df[relevant_columns].isnull().sum())
        return df

    @task(task_id='transform_task')
    def transform_jobs(df):
        """Transform and clean the dataframe"""
        df = clean_data(df)  
        relevant_columns = ['requirements', 'responsibilities', 'level', 'schedule', 'mode', 'contract', 'benefits']
        with pd.option_context('display.max_columns', None,
                            'display.max_rows', None,
                            'display.max_colwidth', None):
            logger.info("Sample data BEFORE cleaning (relevant columns):\n%s", df[relevant_columns].head())
            logger.info("Null counts BEFORE cleaning (relevant columns):\n%s", df[relevant_columns].isnull().sum())
            logger.info("Sample data AFTER cleaning (relevant columns):\n%s", df[relevant_columns].head())
            logger.info("Null counts AFTER cleaning (relevant columns):\n%s", df[relevant_columns].isnull().sum())
        return df

    @task(task_id='load_task')
    def load(df):
        database_url = "postgresql+psycopg2://airflow:airflow@postgresql:5432/jobs_db"
        engine = create_engine(database_url)
        load_to_db(df, engine)
        logging.info("Finished deploying to {job_url} table in the database.")

    end_task = EmptyOperator(task_id='end_task')

    df_extracted = extract_jobs()
    df_transformed = transform_jobs(df_extracted)
    load_result = load(df_transformed)

    start_task >> df_extracted
    load_result >> end_task

get_jobs_etl = get_jobs_etl()
