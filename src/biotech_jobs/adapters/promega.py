
from urllib.parse import urljoin
import hashlib,re
from .base import BaseAdapter
from biotech_jobs.models import Job
JOB_RE=re.compile(r"/jobs/\d+(?:\?|$)",re.I)

class PromegaAdapter(BaseAdapter):
    def fetch(self, company):
        from playwright.sync_api import sync_playwright
        url=company["url"]; found=[]; seen=set(); pages=1
        with sync_playwright() as p:
            b=p.chromium.launch(headless=True); page=b.new_page()
            page.goto(url,wait_until="domcontentloaded",timeout=max(45000,self.timeout*1000))
            page.wait_for_timeout(3500)
            for _ in range(12):
                for __ in range(3):
                    try:
                        page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
                        page.wait_for_timeout(500)
                    except Exception: pass
                for a in page.locator("a").all():
                    try:
                        href=a.get_attribute("href") or ""; label=(a.inner_text() or "").strip()
                    except Exception: continue
                    full=urljoin(page.url,href)
                    if JOB_RE.search(full) and full not in seen and label:
                        seen.add(full); found.append((label,full))
                try:
                    nxt=page.get_by_text(re.compile(r"^Next",re.I))
                    if not nxt.count(): break
                    nxt.first.click(); page.wait_for_timeout(1000); pages+=1
                except Exception: break
            b.close()
        self.last_stats={"pages":pages,"details_enriched":0,"links_discovered":len(found)}
        for label,href in found:
            yield Job(company=company["name"],title=label,location="",url=href,
                source="promega",source_id=hashlib.sha1(href.encode()).hexdigest()[:20],
                description="",raw={"board_url":url})
