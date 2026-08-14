
from __future__ import annotations
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib, re
from .base import BaseAdapter
from biotech_jobs.models import Job

class JazzHRAdapter(BaseAdapter):
    """Collector for JazzHR-hosted applytojob.com career pages."""
    def fetch(self, company: dict):
        url=company["url"]
        r=self.session.get(url,timeout=self.timeout); r.raise_for_status()
        soup=BeautifulSoup(r.text,"html.parser")
        links=[]; seen=set()
        for a in soup.find_all("a",href=True):
            label=a.get_text(" ",strip=True)
            href=urljoin(url,a["href"])
            if not label or href in seen or href.rstrip("/")==url.rstrip("/"):
                continue
            # applytojob job detail links are usually on the same tenant and are not nav links.
            if "applytojob.com" not in href:
                continue
            low=(label+" "+href).lower()
            if any(x in low for x in ("powered by","privacy","login","sign in")):
                continue
            if len(label) > 180:
                continue
            seen.add(href); links.append((label,href))
        self.last_stats={"pages":1,"details_enriched":0,"links_discovered":len(links)}
        used=0
        for label,href in links:
            title=label; location=""; desc=""; raw={"listing_url":url}
            try:
                rr=self.session.get(href,timeout=self.timeout); rr.raise_for_status()
                ss=BeautifulSoup(rr.text,"html.parser")
                h1=ss.find(["h1","h2"])
                if h1 and 0 < len(h1.get_text(" ",strip=True)) < 200:
                    title=h1.get_text(" ",strip=True)
                desc=ss.get_text(" ",strip=True)[:16000]
                # JazzHR detail pages commonly show city/state near the title.
                m=re.search(r"(?:Location|Job Location)\s*[:\-]?\s*([A-Za-z][A-Za-z .,'/\-]{2,100})",desc,re.I)
                if m: location=m.group(1).strip()[:120]
                used += 1
            except Exception:
                pass
            sid=hashlib.sha1(href.encode()).hexdigest()[:20]
            yield Job(company=company["name"],title=title,location=location,url=href,
                      source="jazzhr",source_id=sid,description=desc,raw=raw)
        self.last_stats["details_enriched"]=used
