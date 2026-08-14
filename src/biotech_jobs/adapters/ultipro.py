
from __future__ import annotations
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib, re
from .base import BaseAdapter
from biotech_jobs.models import Job

JOB_HINT=re.compile(r"(JobDetails|JobBoard|Opportunity|job[-_/]?detail|/Job/)",re.I)

class UltiProAdapter(BaseAdapter):
    """Browser-backed collector for public UKG/UltiPro recruiting boards."""
    def fetch(self, company: dict):
        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            raise RuntimeError("Playwright is required for UltiPro boards") from e
        url=company["url"]; out=[]; seen=set(); frames=0
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page()
            page.goto(url,wait_until="domcontentloaded",timeout=max(45000,self.timeout*1000))
            page.wait_for_timeout(int(company.get("render_wait_ms",5000)))
            for _ in range(5):
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(900)
                except Exception: pass
            for frame in page.frames:
                frames += 1
                try: anchors=frame.locator("a").all()
                except Exception: continue
                for a in anchors:
                    try:
                        href=a.get_attribute("href") or ""
                        label=(a.inner_text() or "").strip()
                    except Exception: continue
                    full=urljoin(frame.url or url,href)
                    low=(label+" "+full).lower()
                    if not href or full in seen: continue
                    if JOB_HINT.search(full) or ("recruiting.ultipro.com" in full and label and
                        not any(x in low for x in ("privacy","home","login","company"))):
                        if 2 < len(label) < 220:
                            seen.add(full); out.append((label,full))
            browser.close()
        enriched=0
        for label,href in out:
            title=label; loc=""; desc=""
            try:
                rr=self.session.get(href,timeout=self.timeout); rr.raise_for_status()
                soup=BeautifulSoup(rr.text,"html.parser")
                h=soup.find(["h1","h2"])
                if h and h.get_text(" ",strip=True): title=h.get_text(" ",strip=True)
                desc=soup.get_text(" ",strip=True)[:20000]
                m=re.search(r"(?:Location|Job Location)\s*[:\-]?\s*([A-Za-z0-9 .,'/&()\-]{2,120})",desc,re.I)
                if m: loc=m.group(1).strip()
                enriched += 1
            except Exception:
                pass
            sid=hashlib.sha1(href.encode()).hexdigest()[:20]
            yield Job(company=company["name"],title=title,location=loc,url=href,
                      source="ultipro",source_id=sid,description=desc,
                      raw={"board_url":url})
        self.last_stats={"pages":1,"details_enriched":enriched,"links_discovered":len(out),"frames":frames}
