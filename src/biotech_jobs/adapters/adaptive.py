from __future__ import annotations
import json
import re
from bs4 import BeautifulSoup
from biotech_jobs.adapters.base import AdapterError
from biotech_jobs.models import Job


def _clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def parse_rendered_jobs(html: str, company: dict):
    """Parse a browser-rendered Adaptive careers DOM.

    This function is intentionally separate from browser I/O so it can be tested
    with fixtures and changed quickly if Adaptive updates its page markup.
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # Prefer any JobPosting JSON-LD emitted after hydration.
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try: data = json.loads(tag.string or tag.get_text() or "{}")
        except Exception: continue
        nodes = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []
        for d in nodes:
            if not isinstance(d, dict) or d.get("@type") != "JobPosting": continue
            title = _clean(d.get("title", "")); url = d.get("url", "")
            if not title or not url: continue
            loc = d.get("jobLocation", {})
            if isinstance(loc, list): loc = loc[0] if loc else {}
            addr = loc.get("address", {}) if isinstance(loc, dict) else {}
            location = ", ".join(str(addr.get(k)) for k in ("addressLocality","addressRegion","addressCountry") if addr.get(k))
            desc = _clean(BeautifulSoup(d.get("description", ""), "html.parser").get_text(" "))
            sid = str(d.get("identifier", {}).get("value") if isinstance(d.get("identifier"), dict) else "") or url.rstrip("/").split("/")[-1]
            jobs.append(Job(company=company["name"], title=title, location=location, url=url,
                            source="adaptive", source_id=sid, description=desc,
                            employment_type=_clean(str(d.get("employmentType", ""))), raw=d))
    if jobs:
        return jobs

    # DOM fallback: capture anchors/buttons whose enclosing card contains job-like metadata.
    selectors = company.get("job_link_selector", 'a[href*="career"], a[href*="job"], a[href*="apply"]')
    seen = set()
    for a in soup.select(selectors):
        href = a.get("href", "")
        card = a.find_parent(["article","li","div"]) or a
        text = _clean(card.get_text(" "))
        label = _clean(a.get_text(" "))
        if not href or len(text) < 10: continue
        # Exclude navigation links and generic page chrome.
        if label.lower() in {"careers","career listings","view all career listings","apply now"} and len(text) < 80:
            continue
        title_node = card.find(["h1","h2","h3","h4"])
        title = _clean(title_node.get_text(" ")) if title_node else label
        if not title or title.lower() in {"apply now","learn more","view job"}: continue
        abs_url = href if href.startswith("http") else "https://www.adaptivebiotech.com" + ("" if href.startswith("/") else "/") + href
        key = (title, abs_url)
        if key in seen: continue
        seen.add(key)
        jobs.append(Job(company=company["name"], title=title, location="", url=abs_url,
                        source="adaptive", source_id=abs_url.rstrip("/").split("/")[-1] or title,
                        description=text, raw={"rendered_dom": True}))
    return jobs


class AdaptiveBrowserAdapter:
    """Adaptive Biotechnologies official-careers adapter using Playwright.

    Adaptive's official listing currently requires JavaScript. This adapter renders
    that official page in Chromium and parses the hydrated DOM; it does not use a
    third-party job mirror or bypass access controls.
    """
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def fetch(self, company: dict):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise AdapterError(
                "Adaptive browser adapter requires the optional browser extra. "
                "Install with: pip install -e '.[browser]' && playwright install chromium"
            ) from e
        url = company.get("url") or "https://www.adaptivebiotech.com/career-listings/listing/"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="biotech-job-engine/0.3 (+personal job discovery)")
            page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
            # Allow client-side filtering/list components a short deterministic hydration window.
            page.wait_for_timeout(int(company.get("render_wait_ms", 1500)))
            html = page.content()
            browser.close()
        jobs = parse_rendered_jobs(html, company)
        if not jobs:
            raise AdapterError("Adaptive page rendered but no job postings could be parsed; page markup may have changed")
        yield from jobs
