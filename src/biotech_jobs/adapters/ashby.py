from __future__ import annotations
from .base import BaseAdapter
from biotech_jobs.models import Job


def _s(value) -> str:
    return "" if value is None else str(value)


class AshbyAdapter(BaseAdapter):
    def fetch(self, company: dict):
        board = company["board"]
        url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
        data = self.get_json(url, params={"includeCompensation": "true"})
        for x in data.get("jobs", []):
            if x.get("isListed") is False:
                continue
            comp = x.get("compensation") or {}
            job_url = _s(x.get("jobUrl"))
            source_id = _s(x.get("id")) or job_url
            yield Job(
                company=company["name"], title=_s(x.get("title")),
                location=_s(x.get("location")), url=job_url,
                source="ashby", source_id=source_id,
                description=_s(x.get("descriptionPlain")), department=_s(x.get("department")),
                team=_s(x.get("team")), workplace_type=_s(x.get("workplaceType")),
                employment_type=_s(x.get("employmentType")), published_at=x.get("publishedAt"),
                compensation=_s(comp.get("compensationTierSummary")) if isinstance(comp, dict) else "", raw=x,
            )
