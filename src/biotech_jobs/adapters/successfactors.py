from __future__ import annotations
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import hashlib, re
from .base import BaseAdapter
from biotech_jobs.models import Job

JOB_HREF = re.compile(r"/job/.+?/\d+/?(?:\?|$)", re.I)
LOC_RE = re.compile(r"Location:\s*([^\n]+)", re.I)
DATE_RE = re.compile(r"Date:\s*([^\n]+)", re.I)

class SuccessFactorsAdapter(BaseAdapter):
    """SAP SuccessFactors / Jobs2Web public career-site collector."""
    def fetch(self, company: dict):
        base=(company.get("url") or "").rstrip("/") + "/"
        search_url=company.get("search_url") or urljoin(base,"search/")
        page_size=int(company.get("page_size",25)); max_pages=int(company.get("max_pages",20))
        links=[]; seen=set(); pages=0
        for page in range(max_pages):
            start=page*page_size
            params={"q":"","sortColumn":"referencedate","sortDirection":"desc","startrow":start}
            r=self.session.get(search_url,params=params,timeout=self.timeout); r.raise_for_status(); pages+=1
            soup=BeautifulSoup(r.text,"html.parser")
            page_links=[]
            for a in soup.find_all("a",href=True):
                href=urljoin(search_url,a["href"])
                if not JOB_HREF.search(urlparse(href).path): continue
                title=a.get_text(" ",strip=True)
                key=href.split("?")[0]
                if key in seen: continue
                seen.add(key); page_links.append((title,key))
            if not page_links: break
            links.extend(page_links)
            if len(page_links)<page_size: break
        enriched=0
        for label,href in links:
            title=label; location=""; desc=""; published=None
            raw={}
            try:
                rr=self.session.get(href,timeout=self.timeout); rr.raise_for_status()
                ss=BeautifulSoup(rr.text,"html.parser")
                h1=ss.find("h1")
                if h1: title=h1.get_text(" ",strip=True) or title
                text=ss.get_text("\n",strip=True)
                desc=ss.get_text(" ",strip=True)[:24000]
                m=LOC_RE.search(text)
                if m: location=m.group(1).strip()
                d=DATE_RE.search(text)
                if d: published=d.group(1).strip()
                enriched += 1
                raw={"detail_url":href}
            except Exception:
                pass
            if not title: title=href.rstrip('/').split('/')[-2].replace('-',' ')
            sid=href.rstrip('/').split('/')[-1]
            if not sid.isdigit(): sid=hashlib.sha1(href.encode()).hexdigest()[:20]
            yield Job(company=company["name"],title=title[:220],location=location,url=href,
                      source="successfactors",source_id=sid,description=desc,published_at=published,raw=raw)
        self.last_stats={"pages":pages,"listing_links":len(links),"details_enriched":enriched}
