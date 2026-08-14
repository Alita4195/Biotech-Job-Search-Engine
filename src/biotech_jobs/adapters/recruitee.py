from __future__ import annotations
from .base import BaseAdapter
from biotech_jobs.models import Job
from bs4 import BeautifulSoup

class RecruiteeAdapter(BaseAdapter):
    def fetch(self, company: dict):
        board = company["board"]
        data = self.get_json(f"https://{board}.recruitee.com/api/offers/")
        items = data.get("offers") if isinstance(data, dict) else data
        for x in items or []:
            if x.get("status") not in (None, "published"): continue
            locs = x.get("locations") or []
            if isinstance(locs, list):
                loc = "; ".join(i.get("name", "") if isinstance(i, dict) else str(i) for i in locs)
            else: loc = str(locs or x.get("location") or "")
            desc = x.get("description") or x.get("description_html") or ""
            desc = BeautifulSoup(desc, "html.parser").get_text(" ", strip=True)
            yield Job(company=company["name"], title=x.get("title", ""), location=loc,
                      url=x.get("careers_url") or x.get("url") or f"https://{board}.recruitee.com/o/{x.get('slug','')}",
                      source="recruitee", source_id=str(x.get("id") or x.get("slug") or ""),
                      description=desc, department=(x.get("department") or {}).get("name", "") if isinstance(x.get("department"), dict) else str(x.get("department") or ""),
                      employment_type=str(x.get("employment_type") or ""), raw=x)
