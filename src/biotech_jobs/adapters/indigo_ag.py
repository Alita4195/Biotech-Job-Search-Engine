from __future__ import annotations
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib, re
from .base import BaseAdapter
from biotech_jobs.models import Job

JOB_LINK = re.compile(r"job-application|product-mgmt-intern", re.I)

class IndigoAgAdapter(BaseAdapter):
    """Collector for Indigo Ag's server-rendered company careers page."""
    def fetch(self, company: dict):
        url = company.get("url") or "https://www.indigoag.com/careers"
        r = self.session.get(url, timeout=self.timeout); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        seen=set(); jobs=[]
        for a in soup.find_all("a", href=True):
            href=urljoin(url, a["href"])
            if not JOB_LINK.search(href) or href in seen: continue
            title=(a.get_text(" ",strip=True) or "").strip()
            if not title or title.lower() in {"apply here","apply","learn more"}:
                # Indigo's APPLY HERE links sit under the role heading.
                parent=a
                for _ in range(6):
                    parent=parent.parent if parent else None
                    if not parent: break
                    h=parent.find(["h2","h3","h4","h5","h6"])
                    if h and h.get_text(" ",strip=True):
                        title=h.get_text(" ",strip=True); break
            desc=""; loc=""; raw={}
            try:
                rr=self.session.get(href,timeout=self.timeout); rr.raise_for_status()
                ss=BeautifulSoup(rr.text,"html.parser")
                h1=ss.find(["h1","h2"])
                if h1: title=h1.get_text(" ",strip=True) or title
                desc=ss.get_text(" ",strip=True)[:20000]
                raw={"detail_url":href}
            except Exception:
                pass
            if not title: continue
            seen.add(href)
            sid=hashlib.sha1(href.encode()).hexdigest()[:20]
            jobs.append(Job(company=company["name"],title=title[:220],location=loc,url=href,
                            source="indigo_ag",source_id=sid,description=desc,raw=raw))
        self.last_stats={"listing_links":len(jobs),"details_enriched":sum(bool(j.description) for j in jobs)}
        yield from jobs
