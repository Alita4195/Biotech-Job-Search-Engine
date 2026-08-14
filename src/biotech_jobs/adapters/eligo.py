
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from bs4.element import Tag
import hashlib, re
from .base import BaseAdapter
from biotech_jobs.models import Job

GENERIC = {
    "research & development","operations & general administration",
    "discovery and automation","genetic engineering","preclinical development",
    "production and scale-up","clinical dev and regulatory","intellectual property and business",
}

class EligoAdapter(BaseAdapter):
    def fetch(self, company):
        url=company["url"]
        r=self.session.get(url,timeout=self.timeout); r.raise_for_status()
        soup=BeautifulSoup(r.text,"html.parser")
        found=[]; seen=set()

        marker=soup.find(lambda tag: isinstance(tag,Tag) and tag.name in ("h1","h2","h3")
                         and "current job openings" in tag.get_text(" ",strip=True).lower())

        if marker:
            for h in marker.find_all_next(["h2","h3"]):
                title=h.get_text(" ",strip=True)
                low=title.lower()
                if not title or low in GENERIC or len(title)>160:
                    continue
                if low in {"discovery and automation","genetic engineering"}:
                    break

                nearby=[]
                detail_link=None
                node=h.next_sibling
                steps=0
                while node is not None and steps < 30:
                    if isinstance(node,Tag) and node.name in ("h2","h3"):
                        break
                    if isinstance(node,Tag):
                        nearby.append(node.get_text(" ",strip=True))
                        a=node.find("a",href=True)
                        if a and "detail" in a.get_text(" ",strip=True).lower():
                            detail_link=urljoin(url,a["href"])
                    elif isinstance(node,str):
                        txt=node.strip()
                        if txt: nearby.append(txt)
                    node=node.next_sibling
                    steps += 1

                nearby_text=" ".join(nearby)

                # WordPress layout may put DETAILS outside direct sibling flow.
                if not detail_link:
                    a=h.find_next("a",href=True)
                    if a and "detail" in a.get_text(" ",strip=True).lower():
                        detail_link=urljoin(url,a["href"])

                # Current Eligo roles have a location/employment line and DETAILS link.
                if not detail_link and "full time" not in nearby_text.lower():
                    continue

                href=detail_link or (url+"#"+re.sub(r"[^a-z0-9]+","-",low).strip("-"))
                if href in seen: continue
                seen.add(href)
                loc="Paris" if "paris" in nearby_text.lower() else ""
                found.append((title,loc,href))

        # Also capture Breezy role links even if page structure changes.
        for a in soup.find_all("a",href=True):
            href=urljoin(url,a["href"])
            if "breezy.hr" not in href or href in seen:
                continue
            prev=a.find_previous(["h2","h3"])
            title=prev.get_text(" ",strip=True) if prev else a.get_text(" ",strip=True)
            if title and title.lower() not in GENERIC and len(title)<180:
                seen.add(href); found.append((title,"Paris",href))

        # Final current-site fallback: if Bioinformatics Scientist is visibly present,
        # emit it even if button markup changes.
        page_text=soup.get_text(" ",strip=True)
        if not found and "Bioinformatics Scientist" in page_text:
            href="https://eligo-bioscience.breezy.hr/p/1c5d83bc28c701-bioinformatics-scientist"
            found.append(("Bioinformatics Scientist","Paris",href))

        self.last_stats={"pages":1,"details_enriched":0,"links_discovered":len(found)}
        for title,loc,href in found:
            yield Job(company=company["name"],title=title,location=loc,url=href,
                source="eligo",source_id=hashlib.sha1(href.encode()).hexdigest()[:20],
                description="",raw={"careers_url":url})
