
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib,re
from .base import BaseAdapter
from biotech_jobs.models import Job

JOB_RE=re.compile(r"/jobs/\d+/.+?/job",re.I)

class ICIMSAdapter(BaseAdapter):
    def fetch(self, company):
        base=company["url"]; found=[]; seen=set(); pages=0
        for pr in range(int(company.get("max_pages",20))):
            url=base + ("&" if "?" in base else "?") + f"pr={pr}"
            r=self.session.get(url,timeout=self.timeout); r.raise_for_status()
            soup=BeautifulSoup(r.text,"html.parser"); before=len(found); pages+=1
            for a in soup.find_all("a",href=True):
                href=urljoin(url,a["href"]); label=a.get_text(" ",strip=True)
                if JOB_RE.search(href) and href not in seen and label:
                    seen.add(href); found.append((label,href))
            if pr>0 and len(found)==before: break
        self.last_stats={"pages":pages,"details_enriched":0,"links_discovered":len(found)}
        for label,href in found:
            yield Job(company=company["name"],title=label,location="",url=href,
                source="icims",source_id=hashlib.sha1(href.encode()).hexdigest()[:20],
                description="",raw={"board_url":base})
