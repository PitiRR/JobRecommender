import logging
import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from src.constants import SYSTEM_MESSAGE, TimePeriod
from src.utils.transform_utils import extract_sections

# 3. Ensure consistency
# For jsearch results specifically:
# Requirements, benefits, etc. are empty, but they're contained in the description.
# Use LLM to extract? Find the correct section by looking for keywords?

logger = logging.getLogger(__name__)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
        (describe what the function actually cleans)
    """
    # df = df.drop_duplicates(subset=['url'])
    # logger.debug("Dropped duplicates")

    df = df.dropna(subset=['title', 'company','url'])
    logger.debug("Dropped rows with missing title, company, or url")

    logger.debug("Starting extract_features_from_desc")
    for idx, row in df.iterrows():
        if row[['requirements', 'responsibilities', 'benefits']].isna().any():
            logger.warning(f"Row {idx} is missing requirements, responsibilities, or benefits")
            # features = extract_features_from_desc(row)
            # df.at[idx, 'requirements'] = features[0]
            # df.at[idx, 'responsibilities'] = features[1]
            # df.at[idx, 'benefits'] = features[2]
    logger.info("Finished extract_features_from_desc")

    for idx, row in df.iterrows():
        if isinstance(row['salary'], dict) and 'min' in row['salary'] and row['salary']['min'] is not None:
            df.at[idx, 'salary'] = standardize_compensation(row['salary'], TimePeriod.MONTHLY)

    return df

def extract_features_from_desc(row: pd.Series) -> list:
    """
        This function verifies that responsibilities, requirements, and benefits fields are empty.
        If they are, attempt to extract the missing data from the description. 
        It uses extract_sections() to categorize the fields into the list sections.
        For consistency sake, use ai_summarize_list() to summarize the items into keywords.
    """
    requirements = row['requirements']
    responsibilities = row['responsibilities']
    benefits = row['benefits']

    sections = extract_sections(row['description'])


    if row['responsibilities'] is None:
        logger.debug(f'Missing responsibilities! URL: {row["url"]}')
        features = sections['responsibilities']
        if features:
            print(f'row {row.name}, Responsibilities: {features}')
            requirements = ai_summarize_list(f'requirements {", ".join(features)}').split(',')
            print(f'row {row.name}, Responsibilities summarized: {requirements}')

    if row['requirements'] is None:
        logger.debug(f'Missing requirements! URL: {row["url"]}')
        features = sections['requirements']
        if features:
            print(f'row {row.name}, Reqs: {features}')
            responsibilities = ai_summarize_list(f'requirements {", ".join(features)}').split(',')
            print(f'row {row.name}, Reqs summarized: {responsibilities}')

    if row['benefits'] is None:
        logger.debug(f'Missing benefits! URL: {row["url"]}')
        features = sections['benefits']
        if features:
            print(f'row {row.name}, Benefits: {features}')
            benefits = ai_summarize_list(f'benefits {", ".join(features)}').split(',')
            print(f'row {row.name}, Benefits summarized: {benefits}')

    return [requirements, responsibilities, benefits]

def ai_summarize_list(prompt: str) -> str:
    """
    Summarizes a list of job posting items into keywords using LLM.
    Some job postings do not have the relevant sections, and details are found in the description.
    This function accepts a string of responsibilities, requirements, or benefits.
    The keywords are predefined and categorized into requirements/responsibilities and benefits. 
    The function uses an AI model defined in model_name to generate the summary.
    See constants.py for the system instructions.
    Args:
        query (str): String with raw items. This may be any of the 3 categories.
    Returns:
        list: A list of keywords summarizing the input list.
    Raises:
        ValueError: If the input list is empty or not a list.
        Exception: If there is an error in the AI model response.
    Example:
        input_list = [
            "Experience with ETL processes",
            "Knowledge of data warehousing",
            "Health insurance benefits" 
        ]
        summarized_list = ai_summarize_list(input_list)
        # Output: ['ETL', 'Data Warehousing', 'Health Insurance']
    """
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    endpoint = "https://models.inference.ai.azure.com"
    model_name = "gpt-4o"
    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_MESSAGE,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.5,
        top_p=1.0,
        max_tokens=1000,
        model=model_name
    )

    return response.choices[0].message.content # type: ignore

def standardize_compensation(row_salary: dict, period: TimePeriod) -> list[float]:
    """
        Standardize the units of compensation field.
        1. Make the time period uniform
        2. Adjust the salary to reflect that
        3. Standardize the tax (net vs gross)
        4. Adjust the column and trim of redundant data.

        period: The intended target time period for the salary to transform into.
    """
    period_conversion = {
        TimePeriod.HOURLY: {
            'godz': 1,
            'hr': 1,
            'mies': 1/160,
            'mth': 1/160,
            'rok': 1/2080,
            'yr': 1/2080
        },
        TimePeriod.MONTHLY: {
            'godz': 160,
            'hr': 160,
            'mies': 1,
            'mth': 1,
            'rok': 1/12,
            'yr': 1/12
        },
        TimePeriod.YEARLY: {
            'godz': 2080,
            'hr': 2080,
            'mies': 12,
            'mth': 12,
            'rok': 1,
            'yr': 1
        }
    }

    # Remove trailing dots and whitespace from row's period
    current_period = row_salary['period'].strip().rstrip('.')
    # Get the conversion factor for the current period
    conversion_factor = period_conversion[period].get(current_period, 1)
    logger.debug(f"Standardizing salary: Conversion factor {conversion_factor}.")
    salary = [
        float(row_salary['min'] * conversion_factor),
        float(row_salary['max'] * conversion_factor)
    ]

    logger.debug(f"Standardizing salary: Got {row_salary['min']}-{row_salary['max']} {current_period}, converting to {salary} {period}.")
    return salary
