
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib
from .base import BaseAdapter
from biotech_jobs.models import Job

class JobviteAdapter(BaseAdapter):
    def fetch(self, company):
        url=company["url"]
        r=self.session.get(url,timeout=self.timeout); r.raise_for_status()
        soup=BeautifulSoup(r.text,"html.parser")
        found=[]; seen=set()
        for a in soup.find_all("a",href=True):
            href=urljoin(url,a["href"]); label=a.get_text(" ",strip=True)
            if "/job/" in href and href not in seen and label:
                seen.add(href); found.append((label,href))
        self.last_stats={"pages":1,"details_enriched":0,"links_discovered":len(found)}
        for label,href in found:
            yield Job(company=company["name"],title=label,location="",url=href,
                source="jobvite",source_id=hashlib.sha1(href.encode()).hexdigest()[:20],
                description="",raw={"board_url":url})
