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
    sal_min : int
        Minimum salary provided in the range. Represented in monthly salary.
    sal_max : int
        Maximum salary provided in the range. Represented in monthly salary.
    url : str
        The URL of the job posting, where every detail is accessible.
    id : str
        The unique identifier for the job, uses uuid4.
    """
    def __init__(self,
                 title:             str | None,
                 company:           str | None,
                 description:       str | None,
                 location:          str | None,
                 level:             list[str] | None,
                 schedule:          list[str] | None,
                 mode:              list[str] | None,
                 contract:          list[str] | None,
                 requirements:      list[str] | None,
                 responsibilities:  list[str] | None,
                 benefits:          list[str] | None,
                 sal_min:           int | None,
                 sal_max:           int | None,
                 url:               str | None):
        self.added_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.title = title
        self.company = company
        self.location = location if location else None
        self.description = description if description else None
        self.requirements = requirements if requirements else None
        self.responsibilities = responsibilities if responsibilities else None
        self.level = level if level else None
        self.schedule = schedule if schedule else None
        self.mode = mode if mode else None
        self.contract = contract if contract else None
        self.benefits = benefits if benefits else None
        self.sal_min = sal_min if sal_min else None
        self.sal_max = sal_max if sal_max else None
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
            sal_min={self.sal_min},
            sal_max={self.sal_max},
            url={self.url},
            added_date={self.added_date}
            )"""
        )
