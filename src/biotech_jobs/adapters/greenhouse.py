from __future__ import annotations
from bs4 import BeautifulSoup
from .base import BaseAdapter
from biotech_jobs.models import Job
from biotech_jobs.compensation import extract_greenhouse_pay_html

class GreenhouseAdapter(BaseAdapter):
    def fetch(self, company: dict):
        token = company["board"]
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
        data = self.get_json(url, params={"content": "true"})
        for x in data.get("jobs", []):
            soup = BeautifulSoup(x.get("content") or "", "html.parser")
            content = soup.get_text(" ", strip=True)
            # Parse pay transparency from the original HTML before cleanup.
            compensation = extract_greenhouse_pay_html(x.get("content") or "")
            departments = ", ".join(d.get("name", "") for d in x.get("departments", []))
            yield Job(
                company=company["name"], title=x.get("title", ""),
                location=(x.get("location") or {}).get("name", ""),
                url=x.get("absolute_url", ""), source="greenhouse",
                source_id=str(x.get("id", "")), description=content,
                department=departments, updated_at=x.get("updated_at"), compensation=compensation, raw=x,
            )
