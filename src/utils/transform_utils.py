from typing import Dict, List
from src.constants import SECTION_DEFS

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
