import os
import time
from typing import Dict, List

from dotenv import load_dotenv
from src.constants import SECTION_DEFS, SYSTEM_MESSAGE
import openai
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

def extract_sections(desc: str) -> Dict[str, List[str]]:
    """
    Extract responsibilities, requirements/qualifications and benefits sections from the description
    using header definitions and bulletpoint detection.
    Args:
        desc (str): The job description.
    Returns:
        sections (Dict[str, List[str]]): Dictionary, where key is one of constants.SECTION_DEFS 
            and value is a list of lines
    Example:
        desc = \"\"\"
            Qualifications: 
                * At least 2 years of experience with ETL processes
                * Knowledge of data warehousing
            \"\"\"
        # Output: {'Qualifications': ['At least 2 years of experience with ETL processes', 
        #           'Knowledge of data warehousing']}
    """

    # Define section headers with possible variations


    sections = {k: [] for k in SECTION_DEFS}
    current_section = None
    bullet_chars = ('•', '-', '*')
    # A tuple so that str.startswith can parse it

    for line in (l.strip() for l in desc.split('\n')):
        formatted_line = line.lower().rstrip(':')
        found_section = next(
            (section for section, headers in SECTION_DEFS.items()
             if formatted_line in headers),
            None
        )

        if found_section:
            current_section = found_section
        elif current_section and line.startswith(bullet_chars):
            sections[current_section].append(line)

    return sections

class RateLimitedStandardizer:
    """
    Manages state for applying a function (like an API call)
    element-wise with rate limiting.
    """
    def __init__(self, rpm=15):
        self.rpm = rpm
        # Use monotonic time for consistent rate calculation
        self.call_timestamps = []
        logging.info(f"RateLimitedStandardizer initialized with RPM: {self.rpm}")

    def _wait_if_needed(self):
        """Checks rate limit and sleeps if necessary."""
        now = time.monotonic()
        # Remove timestamps older than 60 seconds
        self.call_timestamps = [t for t in self.call_timestamps if now - t < 60]

        if len(self.call_timestamps) >= self.rpm:
            # Calculate how long until the oldest call expires
            wait_time = 60 - (now - self.call_timestamps[0])
            logging.warning(f"Rate limit ({self.rpm}/min) reached. Waiting for {wait_time:.2f} seconds...")
            print(f"Rate limit reached. Waiting for {wait_time:.2f} seconds...") # Also print to console
            time.sleep(max(0, wait_time) + 0.1) # Sleep until limit allows + small buffer
            # Re-filter timestamps after waiting, as time has passed
            now = time.monotonic()
            self.call_timestamps = [t for t in self.call_timestamps if now - t < 60]

    def process_value(self, original_value, feature_name):
        """
        Applies the AI summarization with rate limiting check.
        To be called via .apply().
        """
        # --- 1. Skip if value is None or empty list ---
        if original_value is None or original_value == []:
            return original_value # Return unchanged

        # --- 2. Handle Rate Limiting ---
        self._wait_if_needed()

        # --- 3. Prepare input and call external function ---
        input_str = f"{feature_name} {original_value}"
        logger.info(f"Processing feature '{feature_name}' (rate limit calls = {len(self.call_timestamps)})...")

        try:
            # Record timestamp *before* the potentially long call
            self.call_timestamps.append(time.monotonic())
            # THE ACTUAL EXTERNAL CALL
            processed_value = ai_summarize_list(input_str)
            logger.info(f"Successfully processed feature '{feature_name}'.")
            return processed_value
        except Exception as e:
            logger.error(f"Error processing feature '{feature_name}' with input '{str(input_str)[:100]}...': {e}", exc_info=True)
            # Decide error handling: return original value? None? An error marker?
            return original_value # Example: return original value on error
        
def ai_summarize_list(prompt: str) -> str | None:
    """
    Summarizes a list of job posting items into keywords using LLM.
    Some job postings do not have the relevant sections, and details are found in the description.
    This function accepts a string of responsibilities, requirements, or benefits.
    The keywords are predefined and categorized into requirements/responsibilities and benefits. 
    The function uses an AI model defined in model_name to generate the summary.
    See constants.py for the system instructions.
    Args:
        prompt (str): String with pre-processed items. This may be any of the 3 categories.
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
    client = OpenAI(
        api_key=os.getenv('GEMINI_API_KEY'),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    try:
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content
    except openai.APIError as e:
        #Handle API error here, e.g. retry or log
        logger.warning(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.APIConnectionError as e:
        #Handle connection error here
        logger.warning(f"Failed to connect to OpenAI API: {e}")
        pass
    except openai.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
        logger.warning(f"OpenAI API request exceeded rate limit: {e}")
        pass
    return None
