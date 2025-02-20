import logging
import os

import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv

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

logger = logging.getLogger(__name__)

def extract_from_jsearch() -> list:
    """
    This function extracts Jobs using rapidapi Jsearch API. It utilizes Google Jobs.
    """
    load_dotenv()
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    rapidapi_host = os.getenv('RAPIDAPI_HOST')

    url = f"https://{rapidapi_host}/search"

    querystring = JSEARCH_QUERY
    # Google is not supporting country: pl, however this does the trick for the most part.

    headers = {
        'x-rapidapi-key': f"{rapidapi_key}",
        'x-rapidapi-host': f"{rapidapi_host}"
    }

    logger.info(f"Running {url}")
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
            logger.debug(f"Jsearch API: successfully added a job. Count: {len(jobs)}")
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

    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        jobs = []
        # Keep only the div with listings
        results = soup.find_all('div', {'data-test': ['positioned-offer', 'default-offer']})

        for job in results:
            company = job.find('h3', {'data-test':'text-company-name'}).text.strip()
            location = job.find('h4', {'data-test':'text-region'}).text.strip()
            job_url = job.a.get('href')

            # Extract remaining required information
            if job_url is not None:
                if job_url.startswith('https://pracodawcy.pracuj.pl/'):
                    continue
                job_response = requests.get(job.a.get('href'), timeout=10)
                if job_response.status_code == 200:
                    soup = BeautifulSoup(job_response.content, 'html.parser')

                    title = company = desc = location = job_url = ""
                    level = schedule = mode = requirements = responsibilities = benefits = contract = []
                    salary = {}


                    title_tag = soup.select_one('h1[data-scroll-id="job-title"]')
                    if title_tag:
                        title = title_tag.text.strip()

                    level_tag = soup.select_one('li[data-scroll-id="position-levels"] div[data-test="offer-badge-title"]')
                    if level_tag:
                        level = extract_job_level(level_tag.get_text(strip=True).lower())

                    raw_contract_tag = soup.select_one('li[data-scroll-id="contract-types"] div[data-test="offer-badge-title"]')
                    if raw_contract_tag:
                        contract = extract_contract_type(raw_contract_tag.get_text(strip=True).lower())

                    raw_desc = soup.select_one('ul[data-test="text-about-project"]')
                    if raw_desc:
                        desc = extract_desc(raw_desc)

                    raw_mode_tag = soup.select_one('li[data-scroll-id="work-modes"] div[data-test="offer-badge-title"]')
                    if raw_mode_tag:
                        mode_list = list(raw_mode_tag.get_text(strip=True).lower().split(','))
                        mode = extract_mode(mode_list)

                    raw_schedule_tag = soup.select_one('li[data-scroll-id="work-schedules"] div[data-test="offer-badge-title"]')
                    if raw_schedule_tag:
                        schedule_list = list(raw_schedule_tag.get_text(strip=True).lower().split(','))
                        schedule = extract_schedule(schedule_list) # type: ignore

                    raw_comp_tag = soup.select_one('div[data-test="section-salaryPerContractType"]')
                    if raw_comp_tag:
                        salary = extract_compensation(raw_comp_tag)

                    raw_resp_tags = soup.select_one('section[data-test="section-responsibilities"]')
                    if raw_resp_tags:
                        raw_resp_list = raw_resp_tags.select('li')
                        if raw_resp_list:
                            responsibilities = extract_fmt_list_items(raw_resp_list)

                    raw_reqs_tags = soup.select_one('section[data-test="section-requirements"]')
                    if raw_reqs_tags:
                        raw_reqs_list = raw_reqs_tags.select('li')
                        if raw_reqs_list:
                            requirements = extract_fmt_list_items(raw_reqs_list)

                    raw_benefits_list = soup.select_one('section[data-test="section-offered"]') or \
                                        soup.select_one('section[data-test="section-benefits"]')
                    if raw_benefits_list:
                        benefits = extract_benefits(raw_benefits_list)


                    jobs.append(
                        Job(
                            title = title,
                            company = company,
                            location = location,
                            description = desc,
                            mode = mode,
                            contract = contract,
                            level = level,
                            schedule = schedule,
                            salary = salary,
                            responsibilities = responsibilities,
                            requirements = requirements,
                            benefits = benefits,
                            url = job_url
                        ))
                else:
                    logger.error("Failed to retrieve job details from %s, status code: %s", job.a.get('href'), job_response.status_code)
            logger.debug(f"Successfully added a job. Count: {len(jobs)}")
    else:
        logger.error(f"Failed to retrieve data from {url}, status code: {response.status_code}")
    return jobs
