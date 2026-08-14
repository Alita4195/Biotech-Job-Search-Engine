from __future__ import annotations
from .base import BaseAdapter
from biotech_jobs.models import Job

class LeverAdapter(BaseAdapter):
    def fetch(self, company: dict):
        site = company["board"]
        url = f"https://api.lever.co/v0/postings/{site}"
        data = self.get_json(url, params={"mode": "json"})
        for x in data:
            cats = x.get("categories") or {}
            description = "\n".join(filter(None, [x.get("descriptionPlain"), x.get("additionalPlain")]))
            salary = x.get("salaryRange") or {}
            salary_text = ""
            if salary:
                salary_text = f"{salary.get('currency','')} {salary.get('min','')}-{salary.get('max','')} {salary.get('interval','')}".strip()
            yield Job(
                company=company["name"], title=x.get("text", ""),
                location=cats.get("location", ""), url=x.get("hostedUrl", ""),
                source="lever", source_id=str(x.get("id", "")),
                description=description, department=cats.get("department", ""),
                team=cats.get("team", ""), workplace_type=x.get("workplaceType", ""),
                employment_type=cats.get("commitment", ""), compensation=salary_text, raw=x,
            )
