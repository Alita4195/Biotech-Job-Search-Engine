from __future__ import annotations
from .base import BaseAdapter
from biotech_jobs.models import Job
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib


def _txt(v):
    if v is None: return ""
    if isinstance(v, dict): return str(v.get("label") or v.get("name") or "")
    return str(v)

class SmartRecruitersAdapter(BaseAdapter):
    """SmartRecruiters public-posting collector.

    Uses the Posting API when the tenant permits public access and falls back to the
    server-rendered SmartRecruiters career page when an account requires API auth.
    """
    def fetch(self, company: dict):
        ident = company["board"]
        try:
            yield from self._fetch_api(company, ident)
            return
        except Exception:
            yield from self._fetch_career_page(company, ident)

    def _fetch_api(self, company, ident):
        limit = min(int(company.get("page_size", 100)), 100)
        offset = 0
        emitted = 0
        while True:
            url = f"https://api.smartrecruiters.com/v1/companies/{ident}/postings"
            data = self.get_json(url, params={"limit": limit, "offset": offset, "destination": "PUBLIC"})
            items = data.get("content", []) or []
            if not items: break
            for x in items:
                pid = str(x.get("uuid") or x.get("id") or "")
                detail = x
                if pid and self.should_enrich_title(x.get("name", ""), company):
                    try:
                        detail = self.get_json(f"https://api.smartrecruiters.com/v1/companies/{ident}/postings/{pid}")
                    except Exception:
                        detail = x
                loc = detail.get("location") or x.get("location") or {}
                loc_text = ", ".join(filter(None, [loc.get("city"), loc.get("region"), loc.get("country")])) if isinstance(loc, dict) else _txt(loc)
                sections = detail.get("jobAd", {}).get("sections", {}) if isinstance(detail.get("jobAd"), dict) else {}
                desc_parts = []
                for val in sections.values() if isinstance(sections, dict) else []:
                    if isinstance(val, dict): desc_parts.append(_txt(val.get("text") or val.get("title")))
                    elif isinstance(val, list): desc_parts.extend(_txt(i.get("text") if isinstance(i, dict) else i) for i in val)
                desc = BeautifulSoup("\n".join(filter(None, desc_parts)), "html.parser").get_text(" ", strip=True)
                yield Job(company=company["name"], title=detail.get("name") or x.get("name", ""),
                          location=loc_text, url=detail.get("applyUrl") or detail.get("ref") or x.get("ref", ""),
                          source="smartrecruiters", source_id=pid,
                          description=desc, department=_txt(detail.get("department") or x.get("department")),
                          workplace_type=_txt(loc.get("remote") if isinstance(loc, dict) else ""),
                          employment_type=_txt(detail.get("typeOfEmployment") or x.get("typeOfEmployment")),
                          published_at=detail.get("releasedDate") or x.get("releasedDate"), raw=detail)
                emitted += 1
            offset += len(items)
            if len(items) < limit or offset >= int(data.get("totalFound") or offset): break
        if emitted == 0:
            raise RuntimeError("SmartRecruiters API returned zero public postings")

    def _fetch_career_page(self, company, ident):
        base = company.get("url") or f"https://careers.smartrecruiters.com/{ident}"
        r = self.session.get(base, timeout=self.timeout); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        seen=set()
        for a in soup.find_all("a", href=True):
            text=a.get_text(" ", strip=True)
            href=urljoin(base,a["href"])
            if not text or href in seen: continue
            if "smartrecruiters.com" not in href or not any(k in href.lower() for k in ["/job", "/position", "apply"]): continue
            seen.add(href)
            sid=hashlib.sha1(href.encode()).hexdigest()[:16]
            yield Job(company=company["name"], title=text[:180], location="", url=href,
                      source="smartrecruiters", source_id=sid, description="")
