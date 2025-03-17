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

#FIXME: below
# [2025-03-16, 20:50:43 UTC] {xcom.py:690} ERROR - ('cannot mix list and non-list, non-null values', 'Conversion failed for column salary with type object'). If you are using pickle instead of JSON for XCom, then you need to enable pickle support for XCom in your *** config or make sure to decorate your object with attr.
# [2025-03-16, 20:50:43 UTC] {taskinstance.py:3313} ERROR - Task failed with exception
# Traceback (most recent call last):
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/models/taskinstance.py", line 790, in _execute_task
#     task_instance.xcom_push(key=XCOM_RETURN_KEY, value=xcom_value, session=session_or_null)
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/utils/session.py", line 94, in wrapper
#     return func(*args, **kwargs)
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/models/taskinstance.py", line 3645, in xcom_push
#     XCom.set(
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/api_internal/internal_api_call.py", line 166, in wrapper
#     return func(*args, **kwargs)
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/utils/session.py", line 94, in wrapper
#     return func(*args, **kwargs)
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/models/xcom.py", line 249, in set
#     value = cls.serialize_value(
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/models/xcom.py", line 688, in serialize_value
#     return json.dumps(value, cls=XComEncoder).encode("UTF-8")
#   File "/usr/local/lib/python3.9/json/__init__.py", line 234, in dumps
#     return cls(
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/utils/json.py", line 105, in encode
#     return super().encode(o)
#   File "/usr/local/lib/python3.9/json/encoder.py", line 199, in encode
#     chunks = self.iterencode(o, _one_shot=True)
#   File "/usr/local/lib/python3.9/json/encoder.py", line 257, in iterencode
#     return _iterencode(o, 0)
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/utils/json.py", line 92, in default
#     return serialize(o)
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/serialization/serde.py", line 149, in serialize
#     data, serialized_classname, version, is_serialized = _serializers[qn].serialize(o)
#   File "/home/airflow/.local/lib/python3.9/site-packages/airflow/serialization/serializers/pandas.py", line 49, in serialize
#     table = pa.Table.from_pandas(o)
#   File "pyarrow/table.pxi", line 4525, in pyarrow.lib.Table.from_pandas
#   File "/home/airflow/.local/lib/python3.9/site-packages/pyarrow/pandas_compat.py", line 611, in dataframe_to_arrays
#     arrays = [convert_column(c, f)
#   File "/home/airflow/.local/lib/python3.9/site-packages/pyarrow/pandas_compat.py", line 611, in <listcomp>
#     arrays = [convert_column(c, f)
#   File "/home/airflow/.local/lib/python3.9/site-packages/pyarrow/pandas_compat.py", line 598, in convert_column
#     raise e
#   File "/home/airflow/.local/lib/python3.9/site-packages/pyarrow/pandas_compat.py", line 592, in convert_column
#     result = pa.array(col, type=type_, from_pandas=True, safe=safe)
#   File "pyarrow/array.pxi", line 345, in pyarrow.lib.array
#   File "pyarrow/array.pxi", line 85, in pyarrow.lib._ndarray_to_array
#   File "pyarrow/error.pxi", line 91, in pyarrow.lib.check_status
# pyarrow.lib.ArrowInvalid: ('cannot mix list and non-list, non-null values', 'Conversion failed for column salary with type object')