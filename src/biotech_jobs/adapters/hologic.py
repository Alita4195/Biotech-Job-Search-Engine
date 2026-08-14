
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib
from .base import BaseAdapter
from biotech_jobs.models import Job

class HologicAdapter(BaseAdapter):
    def fetch(self, company):
        first=company["url"]
        page_base=company.get("page_base",first)
        maxp=int(company.get("max_pages",30))
        found=[]; seen=set(); pages=0
        for pno in range(1,maxp+1):
            url=first if pno==1 else f"{page_base}?page={pno}"
            r=self.session.get(url,timeout=self.timeout); r.raise_for_status()
            soup=BeautifulSoup(r.text,"html.parser"); before=len(found); pages+=1

            for a in soup.find_all("a",href=True):
                label=a.get_text(" ",strip=True)
                if "view detail" not in label.lower():
                    continue
                href=urljoin(url,a["href"])
                if href in seen: continue
                box=a.find_parent(["article","li","div"])
                title=""; loc=""
                if box:
                    h=box.find(["h2","h3","h4","h5"])
                    if h: title=h.get_text(" ",strip=True)
                    if title:
                        txt=box.get_text(" ",strip=True)
                        loc=txt.replace(title,"",1).replace(label,"",1).strip()[:180]
                if not title:
                    prev=a.find_previous(["h2","h3","h4","h5"])
                    if prev: title=prev.get_text(" ",strip=True)
                if title:
                    seen.add(href); found.append((title,loc,href))

            # fallback: heading followed by View details link
            if len(found)==before:
                for h in soup.find_all(["h3","h4"]):
                    title=h.get_text(" ",strip=True)
                    if not title or len(title)>180: continue
                    a=h.find_next("a",href=True)
                    if a and "detail" in a.get_text(" ",strip=True).lower():
                        href=urljoin(url,a["href"])
                        if href not in seen:
                            seen.add(href); found.append((title,"",href))

            if pno>1 and len(found)==before:
                break

        self.last_stats={"pages":pages,"details_enriched":0,"links_discovered":len(found)}
        for title,loc,href in found:
            yield Job(company=company["name"],title=title,location=loc,url=href,
                source="hologic",source_id=hashlib.sha1(href.encode()).hexdigest()[:20],
                description="",raw={"search_url":first})
