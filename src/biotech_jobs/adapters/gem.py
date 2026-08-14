from __future__ import annotations
from .base import BaseAdapter
from biotech_jobs.models import Job

class GemAdapter(BaseAdapter):
    def fetch(self, company: dict):
        board = company["board"]
        data = self.get_json(f"https://api.gem.com/job_board/v0/{board}/job_posts/")
        items = data.get("job_posts") if isinstance(data, dict) else data
        items = items or []
        for x in items:
            loc = x.get("location") or x.get("locations") or ""
            if isinstance(loc, list):
                loc = "; ".join((i.get("name") if isinstance(i, dict) else str(i)) for i in loc)
            elif isinstance(loc, dict): loc = loc.get("name") or loc.get("display_name") or ""
            yield Job(company=company["name"], title=x.get("title", ""), location=str(loc),
                      url=x.get("job_post_url") or x.get("url") or x.get("apply_url") or "",
                      source="gem", source_id=str(x.get("id") or x.get("job_post_id") or ""),
                      description=x.get("description") or x.get("description_plain") or "",
                      department=(x.get("department") or {}).get("name", "") if isinstance(x.get("department"), dict) else str(x.get("department") or ""),
                      workplace_type=str(x.get("workplace_type") or x.get("location_type") or ""),
                      employment_type=str(x.get("employment_type") or ""), raw=x)
