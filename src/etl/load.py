from pandas import DataFrame
import logging

logger = logging.getLogger(__name__)

def load_to_db(df: DataFrame, engine):
    df.to_sql('job_postings', engine, if_exists='replace', index=False)
    logging.info("DataFrame deployed to job_postings table in the database.")