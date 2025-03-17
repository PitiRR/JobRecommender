import logging
import os

import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.constants import JSEARCH_QUERY, PRACUJ_QUERY
from src.models.models import Job
from src.utils.extract_utils import (
    extract_job_level,
    extract_contract_type,
    extract_desc,
    extract_mode,
    extract_schedule,
    extract_compensation,
    extract_fmt_list_items,
    extract_benefits
)

# params list contains parameters in the following order:
# [job name, location, date published, sort, ...]
# websites use different syntax, leading to unique params lists

load_dotenv()
logger = logging.getLogger(__name__)
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

def extract_from_jsearch() -> list:
    """
    This function extracts Jobs using rapidapi Jsearch API. It utilizes Google Jobs.
    """
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    rapidapi_host = os.getenv('RAPIDAPI_HOST')

    url = f"https://{rapidapi_host}/search"

    querystring = JSEARCH_QUERY
    # Google is not supporting country: pl, however this does the trick for the most part.

    headers = {
        'x-rapidapi-key': f"{rapidapi_key}",
        'x-rapidapi-host': f"{rapidapi_host}"
    }
    response = requests.get(url, headers=headers, params=querystring, timeout=10)

    if response.status_code == 200:
        data = response.json().get('data', [])
        jobs = []
        for job_data in data:
            if job_data.get('job_highlights.Benefits'):
                benefits = job_data.get('job_highlights.Benefits')
            elif job_data.get('job_benefits'):
                benefits = job_data.get('job_benefits')
            else: benefits = []
            job = Job(
                title = job_data.get('job_title'),
                company = job_data.get('employer_name'),
                description = job_data.get('job_description'),
                location = job_data.get('job_location'),
                level = [''], # might need to extract from the title
                schedule = job_data.get('job_employment_type'),
                mode = [''], # api doesn't provide field for that
                contract = [''], # api doesn't provide field for that
                responsibilities = job_data.get('job_highlights.Responsibilities'),
                requirements = job_data.get('job_highlights.Qualifications'),
                benefits = benefits,
                salary = {
                    'min': job_data.get('job_min_salary') if job_data.get('job_min_salary') else None,
                    'max': job_data.get('job_max_salary') if job_data.get('job_max_salary') else None,
                    'period': job_data.get('job_salary_period') if job_data.get('job_salary_period') else None
                },
                url = job_data.get('job_apply_link')
            )
            jobs.append(job)
            logger.info(f"Jsearch API: successfully added a job. Count: {len(jobs)}")
        return jobs
    logger.error(f"Failed to retrieve data from {url}, status code: {response.status_code}")
    return []


def extract_from_pracuj() -> list:
    """
    Scrapes job postings data from pracuj.pl
    """
    # Extract job postings from pracuj.pl
    url = PRACUJ_QUERY
    logger.info(f"Running {url}")

    # browser = start_chrome(url, headless=True) # type: ignore
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    if soup:
        jobs = []
        # Keep only the div with listings
        results = soup.find_all('div', {'data-test': ['positioned-offer', 'default-offer']})


        for job in results:
            job_company = job.find('h3', {'data-test':'text-company-name'}).text.strip()
            job_loc = job.find('h4', {'data-test':'text-region'}).text.strip()
            job_url = job.a.get('href')

            # Extract remaining required information
            if job_url is not None:
                soup = None
                if job_url.startswith('https://pracodawcy.pracuj.pl/'):
                    continue
                driver.get(job_url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                if soup.find(job_url):
                    job_title = job_company = job_desc = job_loc = job_url = ""
                    job_seniority_level = job_time_schedule = job_office_mode = job_requirements = job_responsibilities = job_benefits = job_contracts = []
                    job_salaryrange = {}

                    try: 
                        title_tag = soup.select_one('h1[data-scroll-id="job-title"]')
                        job_title = getattr(title_tag, 'text').strip()
                    except (AttributeError, TypeError) as e:
                        job_title = ""

                    try:
                        level_tag = soup.select_one('li[data-scroll-id="position-levels"] div[data-test="offer-badge-title"]')
                        job_seniority_level = extract_job_level(getattr(level_tag, 'text').lower())
                    except (AttributeError, TypeError) as e:
                        job_seniority_level = ['']

                    try:
                        raw_contract_tag = soup.select_one('li[data-scroll-id="contract-types"] div[data-test="offer-badge-title"]')
                        job_contracts = extract_contract_type(getattr(raw_contract_tag, 'text').lower())
                    except (AttributeError, TypeError) as e:
                        job_contracts = ['']
                    try:
                        raw_desc = soup.select_one('ul[data-test="text-about-project"]')
                        job_desc = extract_desc(raw_desc)
                    except (AttributeError, TypeError) as e:
                        job_desc = ""

                    try:
                        raw_mode_tag = soup.select_one('li[data-scroll-id="work-modes"] div[data-test="offer-badge-title"]')
                        mode_list = list(getattr(raw_mode_tag, 'text').strip().lower().split(','))
                        job_office_mode = extract_mode(mode_list)
                    except (AttributeError, TypeError) as e:
                        job_office_mode = ['']

                    try:
                        raw_schedule_tag = soup.select_one('li[data-scroll-id="work-schedules"] div[data-test="offer-badge-title"]')
                        schedule_list = list(getattr(raw_schedule_tag, 'text').strip().lower().split(','))
                        job_time_schedule = extract_schedule(schedule_list) # type: ignore
                    except (AttributeError, TypeError) as e:
                        job_time_schedule = ['']

                    try:
                        raw_comp_tag = soup.select_one('div[data-test="section-salaryPerContractType"]')
                        job_salaryrange = extract_compensation(raw_comp_tag)
                    except (AttributeError, TypeError) as e:
                        job_salaryrange = {}

                    try:
                        raw_resp_tags = soup.select_one('section[data-test="section-responsibilities"]')
                        if raw_resp_tags:
                            job_responsibilities = extract_fmt_list_items(raw_resp_tags.select('li'))
                    except (AttributeError, TypeError) as e:
                        job_responsibilities = []

                    try:
                        raw_reqs_tags = soup.select_one('section[data-test="section-requirements"]')
                        if raw_reqs_tags:
                            job_requirements = extract_fmt_list_items(raw_reqs_tags.select('li'))
                    except (AttributeError, TypeError) as e:
                        job_requirements = []

                    try:
                        raw_benefits_list = soup.select_one('section[data-test="section-offered"]') or \
                                            soup.select_one('section[data-test="section-benefits"]')
                        if raw_benefits_list:
                            job_benefits = extract_benefits(raw_benefits_list)
                    except (AttributeError, TypeError) as e:
                        job_benefits = []


                    jobs.append(
                        Job(
                            title = job_title,
                            company = job_company,
                            location = job_loc,
                            description = job_desc,
                            mode = job_office_mode,
                            contract = job_contracts,
                            level = job_seniority_level,
                            schedule = job_time_schedule,
                            salary = job_salaryrange,
                            responsibilities = job_responsibilities,
                            requirements = job_requirements,
                            benefits = job_benefits,
                            url = job_url
                        ))
                else:
                    logger.error("Failed to retrieve job details from %s, status code: %s", job.a.get('href'), job_response.status_code)
            logger.debug(f"Successfully added a job. Count: {len(jobs)}")
    else:
        logger.error(f"Failed to retrieve data from {url}, status code: {response.status_code}")
    driver.quit()
    return jobs
