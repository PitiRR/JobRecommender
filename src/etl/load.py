import pandas as pd
from pandas import DataFrame
import logging
import numpy as np

logger = logging.getLogger(__name__)

def load_to_db(df: DataFrame, engine):
    # Sometimes jobs are reposted or daily run catches the same job
    # Exclude such jobs
    with engine.connect() as conn:
        existing_urls = pd.read_sql("SELECT url FROM jobs", conn)['url'].tolist()
    df_filtered = df[~df['url'].isin(existing_urls)]


    array_columns = ['requirements', 'responsibilities', 'level', 'schedule', 'mode', 'contract', 'benefits']
    for col in array_columns:
        # Use .apply() to convert each numpy array to a list
        # Handle potential None values gracefully if they exist in your arrays
        # The lambda checks if the value is iterable (like an array) before converting
        df_filtered[col] = df_filtered[col].apply(
            lambda x: list(x) if hasattr(x, '__iter__') and not isinstance(x, (str, bytes)) else x
        )
        # Ensure the column remains object dtype to hold lists
        df_filtered[col] = df_filtered[col].astype(object)


    if not df_filtered.empty:
        df_filtered.to_sql('jobs', engine, if_exists='append', index=False, chunksize=1000)
    else:
        logging.info("No new jobs found to load.")
    logging.info("DataFrame deployed to jobs_db table in the database.")
