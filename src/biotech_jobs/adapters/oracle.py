from __future__ import annotations
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import BaseAdapter
from biotech_jobs.models import Job
import re, json, hashlib

JOB_HREF = re.compile(r"/job/(?:[^/]+/)?\d+/?|/jobs/[^?#]+", re.I)

def _jsonld(soup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            obj=json.loads(tag.string or "{}")
            objs=obj if isinstance(obj,list) else [obj]
            for x in objs:
                if isinstance(x,dict) and x.get("@type")=="JobPosting": return x
        except Exception: pass
    return None

def _job_from_page(company,title,url,html):
    soup=BeautifulSoup(html,"html.parser"); data=_jsonld(soup)
    if data:
        loc=data.get("jobLocation",{})
        if isinstance(loc,list): loc=loc[0] if loc else {}
        addr=(loc.get("address") or {}) if isinstance(loc,dict) else {}
        location=", ".join(filter(None,[addr.get("addressLocality"),addr.get("addressRegion"),addr.get("addressCountry")]))
        desc=BeautifulSoup(data.get("description",""),"html.parser").get_text(" ",strip=True)
        t=data.get("title") or title
        ident=data.get("identifier")
        sid=str(ident.get("value") if isinstance(ident,dict) else ident or url)
        return Job(company=company["name"],title=t,location=location,url=url,source="oracle",source_id=sid,description=desc,raw=data)
    text=soup.get_text(" ",strip=True)
    h=soup.find(["h1","h2"]); t=(h.get_text(" ",strip=True) if h else title) or title
    # Oracle detail pages expose useful Job Info/location text even without JSON-LD.
    return Job(company=company["name"],title=t[:180],location="",url=url,source="oracle",
               source_id=hashlib.sha1(url.encode()).hexdigest()[:20],description=text[:16000],raw={})

class OracleAdapter(BaseAdapter):
    """Oracle Candidate Experience collector with optional Playwright fallback.

    Plain HTTP is attempted first. Oracle CE often renders listings only after JavaScript;
    when `browser_fallback: true`, a headless Chromium page is used only if HTTP finds no jobs.
    """
    def _http_links(self,base,max_pages):
        seen=[]
        for page in range(1,max_pages+1):
            params={} if page==1 else {"page":page}
            r=self.session.get(base,params=params,timeout=self.timeout); r.raise_for_status()
            soup=BeautifulSoup(r.text,"html.parser"); found=[]
            for a in soup.find_all("a",href=True):
                href=a["href"]; text=a.get_text(" ",strip=True)
                if JOB_HREF.search(href) and text:
                    full=urljoin(base,href)
                    if full not in [u for _,u in seen]: found.append((text,full))
            if not found: break
            seen.extend(found)
        return seen

    def _browser_links(self,base):
        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            raise RuntimeError("Oracle browser fallback requires playwright; install the browser extra") from e
        out=[]; seen=set()
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            page=browser.new_page()
            page.goto(base,wait_until="domcontentloaded",timeout=max(30000,self.timeout*1000))
            try: page.wait_for_timeout(2500)
            except Exception: pass
            rendered_anchor_count=0
            rendered_href_matches=0
            for _ in range(10):
                anchors=page.locator("a").all()
                rendered_anchor_count=max(rendered_anchor_count,len(anchors))
                for a in anchors:
                    try:
                        href=a.get_attribute("href") or ""; label=(a.inner_text() or "").strip()
                    except Exception: continue
                    if href and JOB_HREF.search(href):
                        rendered_href_matches += 1
                        full=urljoin(base,href)
                        if full not in seen:
                            seen.add(full); out.append((label or "Oracle job",full))
                try:
                    html=page.content()
                    soup=BeautifulSoup(html,"html.parser")
                    for a in soup.find_all("a",href=True):
                        href=a.get("href","")
                        if JOB_HREF.search(href):
                            rendered_href_matches += 1
                            full=urljoin(base,href)
                            if full not in seen:
                                seen.add(full); out.append((a.get_text(" ",strip=True) or "Oracle job",full))
                except Exception:
                    pass
                try: page.evaluate("window.scrollTo(0, document.body.scrollHeight)"); page.wait_for_timeout(1000)
                except Exception: pass
            self._browser_debug={"anchors":rendered_anchor_count,"job_href_matches":rendered_href_matches,"unique_jobs":len(out)}
            browser.close()
        return out

    def fetch(self,company:dict):
        base=company["url"]; max_pages=int(company.get("max_pages",10))
        links=self._http_links(base,max_pages)
        used_browser=False
        if not links and company.get("browser_fallback"):
            links=self._browser_links(base); used_browser=True
        self.last_stats={"pages": max_pages if links else 1, "details_enriched":0, "browser_fallback":used_browser}
        if used_browser and hasattr(self,"_browser_debug"):
            self.last_stats.update({"oracle_anchors":self._browser_debug.get("anchors",0),
                                    "oracle_job_href_matches":self._browser_debug.get("job_href_matches",0),
                                    "oracle_unique_jobs":self._browser_debug.get("unique_jobs",0)})
        for title,url in links:
            try:
                r=self.session.get(url,timeout=self.timeout); r.raise_for_status()
                self.last_stats["details_enriched"]+=1
                yield _job_from_page(company,title,url,r.text)
            except Exception:
                yield Job(company=company["name"],title=title,location="",url=url,source="oracle",source_id=url,description="")
