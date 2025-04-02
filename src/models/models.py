from datetime import datetime, timezone

class Job:
    """
    Represents a single job posting.

    Attributes:
    ----------
    title : str
        The title of the job used in the source.
    company : str
        The company offering the job.
    description : str
        The job description at the source.
    location : str
        The location of the job/office.
    level : list
        The job level (e.g., junior, mid, senior). See constants.py for possible values.
    schedule : list
        The job schedule (e.g., full-time, part-time). See constants.py for possible values.
    mode : list
        The work mode (e.g., remote, office, hybrid). See constants.py for possible values.
    contract : list
        The contract type (e.g., permanent, b2b). See constants.py for possible values.
    responsibilities : list
        The responsibilities of the job, ie. what the employee will be doing.
    requirements : list
        The requirements for the job, ie. what the employee should have already.
    benefits : list
        The benefits offered by the job.
    salary : str
        The salary range for the job. Represented in yearly salary.
    url : str
        The URL of the job posting, where every detail is accessible.
    id : str
        The unique identifier for the job, uses uuid4.
    """
    def __init__(self,
                 title:             str,
                 company:           str,
                 description:       str,
                 location:          str,
                 level:             list[str],
                 schedule:          list[str],
                 mode:              list[str],
                 contract:          list[str],
                 requirements:      list[str],
                 responsibilities:  list[str],
                 benefits:          list[str],
                 salary:            list[int],
                 url:               str):
        self.added_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.title = title
        self.company = company
        self.location = location if location else ""
        self.description = description if description else ""
        self.requirements = requirements if requirements else []
        self.responsibilities = responsibilities if responsibilities else []
        self.level = level if level else []
        self.schedule = schedule if schedule else []
        self.mode = mode if mode else []
        self.contract = contract if contract else []
        self.benefits = benefits if benefits else []
        self.salary = salary if salary else []
        self.url = url

    def __repr__(self):
        return (
            f"""Job(
            title={self.title},
            company={self.company},
            description={self.description},
            location={self.location},
            level={self.level},
            schedule={self.schedule},
            mode={self.mode},
            contract={self.contract},
            responsibilities={self.responsibilities},
            requirements={self.requirements},
            benefits={self.benefits},
            url={self.url},
            added_date={self.added_date}
            )"""
        )
