import json
import logging
import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
import openai
from openai import OpenAI

from src.constants import SYSTEM_MESSAGE, TimePeriod
from src.utils.transform_utils import extract_sections

logger = logging.getLogger(__name__)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing values, extract features from desc, and standardize compensation."""
    df = df.drop_duplicates(subset=['url'])
    df = df.dropna(subset=['title', 'company','url'])
    df = remove_empty_lists(df)
    # for idx, row in df.iterrows():
    #     features = extract_features_from_desc(row)
    #     df.at[idx, 'requirements'] = features[0]
    #     df.at[idx, 'responsibilities'] = features[1]
    #     df.at[idx, 'benefits'] = features[2]

    # for idx, row in df.iterrows():
    #     if row[['requirements', 'responsibilities', 'benefits']].isna().any():
    #         logger.warning(f"Row {idx} is missing requirements, responsibilities, or benefits")
    #         features = extract_features_from_desc(row)
    #         df.at[idx, 'requirements'] = features[0]
    #         df.at[idx, 'responsibilities'] = features[1]
    #         df.at[idx, 'benefits'] = features[2]
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
            try:
                requirements = ai_summarize_list(f'requirements {", ".join(features)}').split(',')
            except Exception as e:
                logger.error(f"Error summarizing responsibilities: {e}")
                requirements = []
            print(f'row {row.name}, Responsibilities summarized: {requirements}')

    if row['requirements'] is None:
        logger.debug(f'Missing requirements! URL: {row["url"]}')
        features = sections['requirements']
        if features:
            print(f'row {row.name}, Reqs: {features}')
            try:
                responsibilities = ai_summarize_list(f'requirements {", ".join(features)}').split(',')
            except Exception as e:
                logger.error(f"Error summarizing requirements: {e}")
                responsibilities = []
            print(f'row {row.name}, Reqs summarized: {responsibilities}')

    if row['benefits'] is None:
        logger.debug(f'Missing benefits! URL: {row["url"]}')
        features = sections['benefits']
        if features:
            print(f'row {row.name}, Benefits: {features}')
            try:
                benefits = ai_summarize_list(f'benefits {", ".join(features)}').split(',')
            except Exception as e:
                logger.error(f"Error summarizing benefits: {e}")
                benefits = []
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

    try:
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
        return response.choices[0].message.content
    except openai.APIError as e:
        #Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.APIConnectionError as e:
        #Handle connection error here
        print(f"Failed to connect to OpenAI API: {e}")
        pass
    except openai.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
        print(f"OpenAI API request exceeded rate limit: {e}")
        pass
    return e

def standardize_compensation(compensation: dict, period: TimePeriod) -> list[int]:
    """
        Standardize the units of compensation field.
        1. Make the time period uniform
        2. Adjust the salary to reflect that
        3. Standardize the tax (net vs gross)
        4. Adjust the column and trim of redundant data.
        ---
        compensation = {
            'min': float(min_str) if min_str else None, 
            'max': float(max_str) if max_str else None,
            'currency': currency if currency else None,
            'tax': taxperiod[0] if taxperiod else None,
            'period': taxperiod[1] if taxperiod else None
        }
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

    current_period = compensation['period'].strip().rstrip('.')
    conversion_factor = period_conversion[period].get(current_period, 1)
    
    min_salary = int(compensation['min'] * conversion_factor)
    max_salary = int(compensation.get('max', compensation['min']) * conversion_factor)
    
    return [min_salary, max_salary]

def flatten_lists(df: pd.DataFrame) -> pd.DataFrame:
    list_columns = ['level', 'schedule', 'mode', 'contract', 'requirements', 'responsibilities', 'benefits']
    # Some columns contain nested structures, Xcom zealously converts them - causes nested list error.
    for col in list_columns:
        # Ensure all entries are lists
        df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])
        
        # Flatten nested structures and sanitize strings
        df[col] = df[col].apply(
            lambda lst: [
                str(item)
                .replace("{", "").replace("}", "")  # Remove dict braces
                .replace("#", "")                   # Remove markdown
                .strip()
                for item in lst
            ]
        )
        # Convert list/JSON columns to JSON strings for XCom compatibility
        df[col] = df[col].apply(json.dumps)
    return df

def remove_empty_lists(df: pd.DataFrame) -> pd.DataFrame:
    """Convert actual empty lists [] to None AFTER flattening"""
    array_columns = ['requirements', 'responsibilities', 'level', 'schedule', 'mode', 'contract', 'benefits']
    for col in array_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: None if isinstance(x, list) and not x else x)
    return df
