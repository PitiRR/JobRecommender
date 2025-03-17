import logging

import pandas as pd

from src.models.models import Job
from src.etl.extract import extract_from_jsearch, extract_from_pracuj
from src.etl.transform import clean_data
from src.utils.config import start_logger

logger = logging.getLogger(__name__)

def main():
    """
        Entrypoint
    """
    start_logger()
    jsearch_results:list[Job] = extract_from_jsearch()
    logger.info("Finished jsearch_results")
    pracujpl_results:list[Job] = extract_from_pracuj()
    logger.info("Finished extract_from_pracuj")

    # # Convert Job objects to dictionaries parsable by df
    data = [job.__dict__ for job in jsearch_results + pracujpl_results]
    df = pd.DataFrame(data)
    df = clean_data(df)
    #TODO https://www.startdataengineering.com/post/data-engineering-project-for-beginners-batch-edition/
if __name__ == "__main__":
    main()