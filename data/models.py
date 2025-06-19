# data/models.py

from datetime import datetime
from typing import List

class JobPosting:
    title: str
    company: str
    location: str
    url: str
    date_posted: datetime
    role_type: str
    majors: List[str]
    description: str
    source: str
    posted_to_discord: bool
