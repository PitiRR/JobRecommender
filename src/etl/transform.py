import json
import logging
import os
from typing import Optional

import pandas as pd

from src.constants import TimePeriod
from src.utils.transform_utils import ai_summarize_list, extract_sections, RateLimitedStandardizer

logger = logging.getLogger(__name__)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing values, extract features from desc, and standardize compensation."""
    df = df.drop_duplicates(subset=['url'])
    df = df.dropna(subset=['title', 'company','url'])
    df = remove_empty_lists(df)
    df = transform_missing_features(df)
    df = standardize_features(df)

    return df

def standardize_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize the responsibilities, requirements and benefits in the DataFrame
    by applying my_func to each relevant cell.
    """
    df = df.copy()
    features = ['requirements', 'responsibilities', 'benefits']
    standardizer = RateLimitedStandardizer(rpm=15)
    for feature in features:
        if feature in df.columns:
            logger.info(f"--- Standardizing column: {feature} ---")
            df[feature] = df[feature].apply(
                lambda value: standardizer.process_value(value, feature)
            )
            logger.info(f"--- Finished standardizing column: {feature} ---")
        else:
            logger.warning(f"Column '{feature}' not found.")

    return df

def transform_missing_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform DataFrame by filling missing requirements, responsibilities, and benefits
    from the description field where missing using extract_features_from_desc.

    
    Args:
        df: Input DataFrame with job posting data
        
    Returns:
        DataFrame with filled missing values
    """
    df = df.copy()
    
    missing_mask = df[['requirements', 'responsibilities', 'benefits']].isna().any(axis=1)
    rows_to_process = df[missing_mask]
    
    if rows_to_process.empty:
        return df
        
    for idx in rows_to_process.index:
        try:
            logger.warning(f"Row {idx} is missing requirements, responsibilities, or benefits")
            features = extract_features_from_desc(rows_to_process.loc[idx])
            
            if pd.isna(df.at[idx, 'requirements']):
                df.at[idx, 'requirements'] = features[0]
            if pd.isna(df.at[idx, 'responsibilities']):
                df.at[idx, 'responsibilities'] = features[1]
            if pd.isna(df.at[idx, 'benefits']):
                df.at[idx, 'benefits'] = features[2]
                
        except Exception as e:
            logger.error(f"Error processing row {idx}: {str(e)}")
            continue
            
    return df

def extract_features_from_desc(row: pd.Series) -> Optional[list]:
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
                result = ai_summarize_list(f'requirements {", ".join(features)}')
                requirements = result.split(',') if result else []
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
                result = ai_summarize_list(f'requirements {", ".join(features)}')
                responsibilities = result.split(',') if result else []
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
                result = ai_summarize_list(f'benefits {", ".join(features)}')
                benefits = result.split(',') if result else []
            except Exception as e:
                logger.error(f"Error summarizing benefits: {e}")
                benefits = []
            print(f'row {row.name}, Benefits summarized: {benefits}')

    return [requirements, responsibilities, benefits]

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
