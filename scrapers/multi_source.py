import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup

class JobScraper:
    def __init__(self):
        self.sources = {
            'summer2026_swe_vanshb_internship': { # SWE Internship positions
                'url': 'https://raw.githubusercontent.com/vanshb03/Summer2026-Internships/dev/.github/scripts/listings.json',
                'type': 'json',
                'source_name': 'Summer2026-Internships-Vanshb'
            },
            'summer2026_swe_simplify_internship': {
                'url': 'https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/.github/scripts/listings.json',
                'type': 'json',
                'source_name': 'Summer2026-Internships-SimplifyJobs'
            },
            'jobright_ai_software_internship': {
                'url': 'https://raw.githubusercontent.com/jobright-ai/2025-Software-Engineer-Internship/master/README.md',
                'type': 'markdown_table',
                'source_name': 'JobRight-AI-Software-Internship',
                'table_format': 'jobright'
            },


            'jobright_ai_engineering_internship': { # PM & Engineering Internship positions
                'url': 'https://raw.githubusercontent.com/jobright-ai/2025-Engineer-Internship/master/README.md',
                'type': 'markdown_table',
                'source_name': 'JobRight-AI-Engineering-Internship',
                'table_format': 'jobright'
            },
            'jobright_ai_product_management_internship': { 
                'url': 'https://raw.githubusercontent.com/jobright-ai/2025-Product-Management-Internship/master/README.md',
                'type': 'markdown_table',
                'source_name': 'JobRight-AI-Product-Management-Internship',
                'table_format': 'jobright'
            },


            'newgrad_swe_vanshb': { # SWE New Grad positions
                'url': 'https://raw.githubusercontent.com/vanshb03/New-Grad-2025/dev/.github/scripts/listings.json', 
                'type': 'json',
                'source_name': 'New-Grad-SWE-Vanshb',
            },
            'newgrad_swe_simplify': {
                'url': 'https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json',
                'type': 'json',
                'source_name': 'New-Grad-SWE-SimplifyJobs',
            },
            'new_grad_jobright_ai_swe': {
                'url': 'https://raw.githubusercontent.com/jobright-ai/2025-Software-Engineer-New-Grad/master/README.md',
                'type': 'markdown_table',
                'source_name': 'JobRight-AI-Software-New-Grad',
                'table_format': 'jobright'
            },


            'newgrad_pm_jobright': { # PM & Engineering New Grad positions
                'url': 'https://raw.githubusercontent.com/jobright-ai/2025-Product-Management-Internship/master/README.md',
                'type': 'markdown_table',
                'source_name': 'JobRight-AI-Product-Management-New-Grad',
                'table_format': 'jobright'
            },
            'newgrad_eng_jobright': {
                'url': 'https://raw.githubusercontent.com/jobright-ai/2025-Engineering-New-Grad/master/README.md',
                'type': 'markdown_table',
                'source_name': 'JobRight-AI-Engineering-New-Grad',
                'table_format': 'jobright'
            },
        }

    def fetch_github_json(self, url: str) -> List[Dict]:
        """Fetch JSON data from GitHub raw URL"""
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def fetch_markdown_content(self, url: str) -> str:
        """Fetch markdown content from GitHub"""
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    
    def _strip_html(self, text: str) -> str:
        """Remove any HTML tags before further processing."""
        return BeautifulSoup(text, "html.parser").get_text(separator=", ")

    def _clean_position_text(self, text: str) -> str:
        """Remove markdown formatting and extra spaces from text."""
        text = self._strip_html(text)
        if not text:
            return ""
        # 2. Remove markdown links, emphasis, etc.
        cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        cleaned = re.sub(r'[*_`#]', '', cleaned)
        return cleaned.strip()

    def _extract_url_from_markdown(self, text: str) -> str:
        """Extract URL from markdown link format or plain text"""
        if not text:
            return ""
        markdown_link_match = re.search(r'\[([^\]]*)\]\(([^)]+)\)', text)
        if markdown_link_match:
            return markdown_link_match.group(2).strip()
        url_match = re.search(r'https?://[^\s<>\[\]]+', text)
        if url_match:
            return url_match.group(0).strip()
        if any(keyword in text.lower() for keyword in ['apply', 'link', 'url']):
            return text.strip()
        return ""

    def _parse_date(self, date_str: str) -> datetime:
        """Try to parse various date formats, including incomplete dates like 'Jun 19'"""
        date_str = date_str.strip()
        date_str = re.sub(r'^(posted|updated|added):\s*', '', date_str, flags=re.IGNORECASE)
        date_str = re.sub(r'\s*(ago|old)$', '', date_str, flags=re.IGNORECASE)

        # Handle relative dates like "2 days ago"
        relative_match = re.search(r'(\d+)\s*(day|week|month)s?\s*ago', date_str, re.IGNORECASE)
        if relative_match:
            num = int(relative_match.group(1))
            unit = relative_match.group(2).lower()
            if unit == 'day':
                return datetime.now() - timedelta(days=num)
            elif unit == 'week':
                return datetime.now() - timedelta(weeks=num)
            elif unit == 'month':
                return datetime.now() - timedelta(days=num * 30)

        # Try to parse as 'Jun 19' (month day)
        try:
            date_obj = datetime.strptime(date_str, '%b %d')
            date_obj = date_obj.replace(year=datetime.now().year)
            if date_obj > datetime.now():
                date_obj = date_obj.replace(year=datetime.now().year - 1)
            return date_obj
        except ValueError:
            pass

        # Common date formats
        formats = [
            '%b %d, %Y',      # Dec 18, 2024
            '%B %d, %Y',      # December 18, 2024
            '%m/%d/%Y',       # 12/18/2024
            '%Y-%m-%d',       # 2024-12-18
            '%d-%m-%Y',       # 18-12-2024
            '%m-%d-%Y',       # 12-18-2024
            '%Y/%m/%d',       # 2024/12/18
            '%d/%m/%Y',       # 18/12/2024
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # If all else fails, assume it's recent (within last week)
        return datetime.now() - timedelta(days=7)

    def parse_markdown_table(self, markdown_content: str, table_format: str = 'default') -> List[Dict]:
        jobs = []
        lines = markdown_content.split('\n')
        header_found = False
        last_company = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('|') and line.endswith('|'):
                columns = [col.strip() for col in line[1:-1].split('|')]

                if not header_found:
                    if any(keyword in ' '.join(columns).lower() for keyword in ['company', 'position', 'location', 'application', 'job title']):
                        header_found = True
                        continue

                if header_found and all('---' in col or col == '' for col in columns):
                    continue

                if header_found and len(columns) >= 3:
                    try:
                        if table_format == 'jobright':
                            if len(columns) >= 5:
                                company = columns[0].strip()
                                if company == '↳' and last_company:
                                    company = last_company
                                else:
                                    last_company = company if company and company != '↳' else last_company

                                position = columns[1].strip()
                                location = columns[2].strip()
                                work_model = columns[3].strip()
                                date_posted = columns[4].strip()

                                url = self._extract_url_from_markdown(position)
                                position = self._clean_position_text(position)
                                company = self._clean_position_text(company)

                                if not company or not position or company.lower() in ['company', 'name']:
                                    continue

                                try:
                                    if date_posted:
                                        date_obj = self._parse_date(date_posted)
                                    else:
                                        date_obj = datetime.now()
                                except Exception:
                                    date_obj = datetime.now()

                                job_entry = {
                                    'title': position,
                                    'company_name': company,
                                    'locations': [location] if location and location.lower() not in ['n/a', '', 'remote', 'various'] else [],
                                    'url': url,
                                    'date_posted': int(date_obj.timestamp()),
                                    'work_model': work_model
                                }
                                if not job_entry["url"]:
                                    continue

                                jobs.append(job_entry)
                            else:
                                print(f"WARNING: Skipping row with only {len(columns)} columns: {columns}")
                                continue
                        else:
                            company = columns[0].strip()
                            position = columns[1].strip()
                            location = columns[2].strip() if len(columns) > 2 else ""
                            application_info = columns[3].strip() if len(columns) > 3 else ""
                            date_posted = columns[4].strip() if len(columns) > 4 else ""
                            url = self._extract_url_from_markdown(application_info)
                            work_model = None

                            if not company or not position or company.lower() in ['company', 'name']:
                                continue

                            try:
                                if date_posted:
                                    date_obj = self._parse_date(date_posted)
                                else:
                                    date_obj = datetime.now()
                            except Exception:
                                date_obj = datetime.now()

                            job_entry = {
                                'title': position,
                                'company_name': company,
                                'locations': [location] if location and location.lower() not in ['n/a', '', 'remote', 'various'] else [],
                                'url': url,
                                'date_posted': int(date_obj.timestamp()),
                                'work_model': work_model
                            }
                            jobs.append(job_entry)
                    except Exception as e:
                        print(f"Error parsing row: {line}, Error: {str(e)}")
                        continue

        return jobs

    def map_job(self, json_job: Dict, source_name: str) -> Dict:
        """Map job data to standardized format"""
        if 'date_posted' in json_job and isinstance(json_job['date_posted'], int):
            date_posted = datetime.fromtimestamp(json_job["date_posted"])
        else:
            date_posted = json_job.get('date_posted', datetime.now())

        role_type = ("New Grad" if "New-Grad" in source_name or 
                     "Newgrad" in source_name else "Internship")

        return {
            "title": json_job.get("title", ""),
            "company": json_job.get("company_name", json_job.get("company", "")),
            "location": ", ".join(json_job.get("locations", [])) if json_job.get("locations") else json_job.get("location", ""),
            "url": json_job.get("url", ""),
            "date_posted": date_posted,
            "role_type": role_type,
            "majors": [],
            "description": "",
            "source": source_name,
            "posted_to_discord": False,
            "work_model": json_job.get("work_model", "")
        }

    def filter_recent_jobs(self, jobs: List[Dict], days: int = 7) -> List[Dict]:
        """Filter jobs to only include those posted within the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_jobs = []

        for job in jobs:
            if isinstance(job["date_posted"], int):
                job_date = datetime.fromtimestamp(job["date_posted"])
            else:
                job_date = job["date_posted"]

            if job_date >= cutoff_date:
                recent_jobs.append(job)

        return recent_jobs

    def fetch_all_jobs(self, days: int = 7) -> List[Dict]:
        """Fetch jobs from all configured sources"""
        all_jobs = []

        for source_key, source_config in self.sources.items():
            try:
                print(f"Fetching jobs from {source_config['source_name']}...")

                if source_config['type'] == 'json':
                    raw_jobs = self.fetch_github_json(source_config['url'])
                elif source_config['type'] == 'markdown_table':
                    markdown_content = self.fetch_markdown_content(source_config['url'])
                    table_format = source_config.get('table_format', 'default')
                    raw_jobs = self.parse_markdown_table(markdown_content, table_format)
                else:
                    print(f"Unknown source type: {source_config['type']}")
                    continue

                recent_jobs = self.filter_recent_jobs(raw_jobs, days)
                mapped_jobs = [self.map_job(job, source_config['source_name']) for job in recent_jobs]
                all_jobs.extend(mapped_jobs)
                print(f"Found {len(mapped_jobs)} recent jobs from {source_config['source_name']}")

            except Exception as e:
                print(f"Error fetching from {source_config['source_name']}: {str(e)}")
                continue

        seen_jobs = set()
        unique_jobs = []

        for job in all_jobs:
            if job["url"] not in seen_jobs:
                seen_jobs.add(job["url"])
                unique_jobs.append(job)

        unique_jobs.sort(key=lambda x: x['date_posted'])  # Oldest first
        # CAP TO 100
        if len(unique_jobs) > 300:
            unique_jobs = unique_jobs[-300:]

        print(f"Total unique jobs after deduplication (capped to 300): {len(unique_jobs)}")
        return unique_jobs

# For backward compatibility
def fetch_github_json(url):
    scraper = JobScraper()
    return scraper.fetch_github_json(url)

def map_job(json_job):
    scraper = JobScraper()
    return scraper.map_job(json_job, "GitHub")

def filter_recent_jobs(jobs, days=7):
    scraper = JobScraper()
    return scraper.filter_recent_jobs(jobs, days)

def fetch_and_filter_recent_jobs(url, days=7):
    scraper = JobScraper()
    data = scraper.fetch_github_json(url)
    recent_jobs_raw = scraper.filter_recent_jobs(data, days)
    return [scraper.map_job(job, "GitHub") for job in recent_jobs_raw]
