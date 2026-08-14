from __future__ import annotations
from typing import Iterable
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup
from .base import BaseAdapter, AdapterError
from biotech_jobs.models import Job


class FoundationMedicineAdapter(BaseAdapter):
    """Adapter for Foundation Medicine's public careers search pages.

    The site renders job rows server-side at /jobs/search and supports paginated
    search result pages. We keep this adapter company-specific because the markup
    belongs to Foundation Medicine's careers frontend rather than a reusable ATS API.
    """

    def _get_html(self, url: str):
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.text

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "")).strip()

    def _parse_detail(self, company: dict, url: str) -> Job:
        html = self._get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        title_node = soup.find("h1")
        title = self._clean(title_node.get_text(" ", strip=True) if title_node else "")

        # Careers sites commonly provide structured data even when visible markup varies.
        location = ""
        description = ""
        source_id = ""
        for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                import json
                data = json.loads(tag.string or "{}")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if not isinstance(item, dict) or item.get("@type") != "JobPosting":
                        continue
                    title = item.get("title") or title
                    source_id = str((item.get("identifier") or {}).get("value") or "")
                    description = BeautifulSoup(item.get("description", ""), "html.parser").get_text(" ", strip=True)
                    loc = item.get("jobLocation")
                    if isinstance(loc, list):
                        loc = loc[0] if loc else {}
                    if isinstance(loc, dict):
                        addr = loc.get("address") or {}
                        location = ", ".join(x for x in [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")] if x)
                    return Job(company=company["name"], title=title, location=location, url=url,
                               source="foundation", source_id=source_id or url.rstrip('/').split('/')[-1],
                               description=description, raw={"url": url})
            except Exception:
                pass

        main = soup.find("main") or soup.body
        description = self._clean(main.get_text(" ", strip=True) if main else "")
        if not title:
            title = url.rstrip('/').split('/')[-1].replace('-', ' ')
        return Job(company=company["name"], title=title, location=location, url=url,
                   source="foundation", source_id=source_id or url.rstrip('/').split('/')[-1],
                   description=description, raw={"url": url})

    def fetch(self, company: dict) -> Iterable[Job]:
        base = company.get("url", "https://careers.foundationmedicine.com/jobs/search")
        max_pages = int(company.get("max_pages", 10))
        seen_urls = set()

        for page in range(1, max_pages + 1):
            url = base if page == 1 else f"{base}?page={page}"
            html = self._get_html(url)
            soup = BeautifulSoup(html, "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/jobs/" not in href or "/jobs/search" in href:
                    continue
                absolute = urljoin(base, href)
                if absolute in seen_urls:
                    continue
                text = self._clean(a.get_text(" ", strip=True))
                if not text:
                    continue
                seen_urls.add(absolute)
                links.append(absolute)

            if not links:
                if page == 1:
                    raise AdapterError(f"No Foundation Medicine job links found at {base}")
                break

            for job_url in links:
                try:
                    yield self._parse_detail(company, job_url)
                except Exception:
                    # A listing disappearing between index and detail fetch should not fail the board.
                    continue

            # If there is no visible next-page link, stop after this page.
            next_link = soup.find("a", string=re.compile(r"next", re.I))
            if page > 1 and not next_link:
                # Some pages use numbered pagination only; continue only if this page returned a full set.
                if len(links) < int(company.get("expected_page_size", 30)):
                    break
