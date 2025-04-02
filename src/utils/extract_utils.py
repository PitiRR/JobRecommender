import logging
import re
from typing import Union

from bs4 import ResultSet

from src.constants import EMPLOYMENTS, JOBLEVELS, MODES, SCHEDULES, TimePeriod
from src.etl.transform import standardize_compensation

logger = logging.getLogger(__name__)

def extract_job_level(raw_level_text: str) -> list:
    """

    """
    level = []
    formatted_level_text = [level.strip().lower() for text in re.findall(r'\(.*?\)', raw_level_text)
                            for level in re.sub(r'[()]', '', text).split('/')]
    if formatted_level_text:
        if any(junior_kw in formatted_level_text for junior_kw in JOBLEVELS["junior"]):
            level.append("junior")
        if any(mid_kw in formatted_level_text for mid_kw in JOBLEVELS["mid"]):
            level.append("mid")
        if any(senior_kw in formatted_level_text for senior_kw in JOBLEVELS["senior"]):
            level.append("senior")
        if not level:
            level.append("other")
    logger.debug(f"Extracted available job levels: {level}")
    return level

def extract_contract_type(raw_contract_text: str) -> list[str]:
    contract = []
    if raw_contract_text:
        if any(perma_kw in raw_contract_text for perma_kw in EMPLOYMENTS["permanent"]):
            contract.append("permanent")
        if any(b2b_kw in raw_contract_text for b2b_kw in EMPLOYMENTS["b2b"]):
            contract.append("b2b")
        if not contract:
            contract.append("other")
    logger.debug(f"Extracted available contract types: {contract}")
    return contract

def extract_desc(raw_desc):
    """
        Extract description text from a list of HTML elements.
        The text is split among different list items. This func returns a single, multiline string.
        Useful for further transformations.
    """
    desc = [li.text.strip() for li in raw_desc.find_all('li')]
    logger.debug(f"Extracted description (head): {desc[0]}")
    return '\n'.join(desc)

def extract_mode(raw_mode_text: list[str]) -> list[str]:
    mode = []
    if any(remote_kw in raw_mode_text for remote_kw in MODES["remote"]):
        mode.append("remote")
    if any(office_kw in raw_mode_text for office_kw in MODES["office"]):
        mode.append("office")
    if any(hybrid_kw in raw_mode_text for hybrid_kw in MODES["hybrid"]):
        mode.append("hybrid")
    if any(mobile_kw in raw_mode_text for mobile_kw in MODES["mobile"]):
        mode.append("mobile")
    logger.debug(f"Extracted available work modes: {mode}")
    return mode

def extract_schedule(raw_schedule_text: str) -> list[str]:
    schedule = []
    if raw_schedule_text:
        if any(fulltime_kw in raw_schedule_text for fulltime_kw in SCHEDULES["full-time"]):
            schedule.append("full-time")
        if any(parttime_kw in raw_schedule_text for parttime_kw in SCHEDULES["part-time"]):
            schedule.append("part-time")
        if not schedule:
            schedule.append("other")
    logger.debug(f"Extracted available schedules: {schedule}")
    return schedule

def extract_compensation(raw_compensation_tag) -> list[int]:
    """
        Extract compensation data.
        Most tags contain a salary range (some don't), currency, tax indication and period.
    """
    min_str = max_str = currency = taxperiod = None
    salary_range = []
    earning_amount_div = raw_compensation_tag.find('div', {'data-test': 'text-earningAmount'})
    if earning_amount_div:
        range_parts = re.split(r'[–-]', earning_amount_div.get_text(strip=True))
        if len(range_parts) == 2:
            min_str = re.sub(r'[^\d,.]', '', range_parts[0]).replace(',', '.')
            max_str = re.sub(r'[^\d,.]', '', range_parts[1]).replace(',', '.')
        elif len(range_parts) == 1:
            min_str = re.sub(r'[^\d,.]', '', range_parts[0]).replace(',', '.')
            max_str = min_str
        currency = earning_amount_div.find('div').get_text(strip=True)
        taxperiod = earning_amount_div.find_next_sibling('div').text.split('/')
    compensation = {
        'min': float(min_str) if min_str else None, 
        'max': float(max_str) if max_str else None,
        'currency': currency if currency else None,
        'tax': taxperiod[0] if taxperiod else None,
        'period': taxperiod[1] if taxperiod else None
    }
    if compensation['min']:
        salary_range = standardize_compensation(compensation, TimePeriod.MONTHLY)
    logger.debug(f"Extracted compensation: {compensation}")
    return salary_range

def extract_fmt_list_items(raw_text_list: Union[list, ResultSet]) -> list[str]:
    """Extract preformatted list items. Gets text and strips whitespace from a list of HTML elements."""
    return [li.text.strip() for li in raw_text_list]

def extract_benefits(raw_benefits_list):
    """
        Extract text and clean elements from a list of HTML elements.
        The HTML formatting may differ from offer to offer, this func handles both options.
    """
    if raw_benefits_list:
        formatted_benefits_list = [li.text.strip() for li in raw_benefits_list.find_all('li')] or \
                                  [div.text.strip() for div in raw_benefits_list.find_all('div',
                                  {'data-test': 'text-benefit-title'})]
        logger.debug(f"Extracted benefits (head): {formatted_benefits_list[0]}")
        return formatted_benefits_list
    return []
