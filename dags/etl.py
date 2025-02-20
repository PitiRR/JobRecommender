import logging
import os
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine
from airflow.decorators import dag, task

from dotenv import load_dotenv
from src.etl.extract import extract_from_jsearch, extract_from_pracuj
from src.etl.transform import clean_data
from src.utils.config import start_logger


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 16),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

logger = logging.getLogger(__name__)
load_dotenv()
airflow_email = os.getenv('AIRFLOW_EMAIL')

@dag(
    start_date=datetime(2025, 2, 16),
    schedule="@daily",
    catchup=False,
)
def create_etl_dag(email = airflow_email):
    logging.info("Start task initiated")
    start_logger()

    DATABASE_URL = 'postgresql://airflow:airflow@postgres:5432/airflow_metadata'
    engine = create_engine(DATABASE_URL)

    @task(task_id='start')
    def start():
        """Dummy entrypoint"""
        logger.info("Starting the ETL pipeline...")

    @task(task_id='extract_task')
    def extract():
        jsearch_results = extract_from_jsearch()
        logger.info("Finished extracting jsearch_results")
        pracujpl_results = extract_from_pracuj()
        logger.info("Finished extracting extract_from_pracuj")

        data = [job.__dict__ for job in jsearch_results + pracujpl_results]
        df = pd.DataFrame(data)
        return df

    @task(task_id='transform_task')
    def transform(**context):
        """Transform and clean the dataframe"""
        df = context['task_instance'].xcom_pull(task_ids='extract_task')
        df = clean_data(df)
        return df

    @task(task_id='load_to_db_task')
    def load(**context):
        df = context['task_instance'].xcom_pull(task_ids='transform_task')
        df.to_sql('job_postings', engine, if_exists='replace', index=False)
        logging.info("DataFrame deployed to job_postings table in the database.")

    @task(task_id='end')
    def end():
        """Dummy endpoint"""
        logger.info("...Finishing the ETL pipeline.")

    start_task = start()
    extract_task = extract()
    transform_task = transform()
    load_task = load()
    end_task = end()

    start_task >> extract_task >> transform_task >> load_task >> end_task

ETL_DAG = create_etl_dag()
# TODO fix this based on Data Engineer specialization and official docs
# TODO https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html
# You're doing great Piotr!
