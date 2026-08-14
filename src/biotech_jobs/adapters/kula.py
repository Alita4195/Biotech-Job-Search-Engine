from __future__ import annotations
import json
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from biotech_jobs.adapters.base import BaseAdapter, AdapterError
from biotech_jobs.models import Job


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _jobposting_jsonld(soup: BeautifulSoup):
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(tag.string or tag.get_text() or "{}")
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                return item
            if isinstance(item, dict) and isinstance(item.get("@graph"), list):
                for node in item["@graph"]:
                    if isinstance(node, dict) and node.get("@type") == "JobPosting":
                        return node
    return None


def _jsonld_location(data: dict) -> str:
    loc = data.get("jobLocation")
    if isinstance(loc, list):
        loc = loc[0] if loc else None
    if not isinstance(loc, dict):
        return ""
    addr = loc.get("address", loc)
    if not isinstance(addr, dict):
        return ""
    vals = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
    return ", ".join(str(v) for v in vals if v)


class KulaAdapter(BaseAdapter):
    """Public Kula careers-board adapter.

    Kula boards are server-rendered and expose stable job detail URLs. We discover
    detail links from the board, then prefer schema.org JobPosting JSON-LD on each
    detail page, falling back to conservative DOM/text extraction.
    """

    def fetch(self, company: dict):
        board = company.get("board")
        if not board:
            raise AdapterError("Kula requires company.board, e.g. '10xgenomics'")
        base_url = company.get("url") or f"https://careers.kula.ai/{board}"
        r = self.session.get(base_url, timeout=self.timeout)
        r.raise_for_status()
        links = self._detail_links(r.text, base_url, board)
        if not links:
            raise AdapterError(f"No Kula job links found on {base_url}")
        for url in links:
            try:
                job = self._fetch_detail(company, url)
                if job:
                    yield job
            except Exception:
                # One malformed/removed detail page should not invalidate the board.
                continue

    @staticmethod
    def _detail_links(html: str, base_url: str, board: str):
        soup = BeautifulSoup(html, "html.parser")
        out = []
        seen = set()
        pattern = re.compile(rf"^/{re.escape(board)}/(\d+)/?$")
        for a in soup.find_all("a", href=True):
            href = a["href"].split("?", 1)[0].rstrip("/")
            parsed = urlparse(href)
            path = parsed.path if parsed.scheme else href
            if pattern.match(path):
                url = urljoin(base_url + "/", path)
                if url not in seen:
                    seen.add(url); out.append(url)
        return out

    def _fetch_detail(self, company: dict, url: str):
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        data = _jobposting_jsonld(soup)
        source_id = url.rstrip("/").split("/")[-1]
        if data:
            desc_html = data.get("description") or ""
            desc = _clean(BeautifulSoup(desc_html, "html.parser").get_text(" "))
            title = _clean(data.get("title") or "")
            if not title:
                heading = soup.find("h1") or soup.find("h2")
                title = _clean(heading.get_text(" ") if heading else "")
            if not title:
                return None
            location = _jsonld_location(data)
            emp = data.get("employmentType") or ""
            if isinstance(emp, list): emp = ", ".join(emp)
            return Job(
                company=company["name"], title=title, location=location, url=url,
                source="kula", source_id=source_id, description=desc,
                department="", workplace_type="", employment_type=_clean(str(emp)),
                published_at=data.get("datePosted"), updated_at=data.get("validThrough"),
                compensation=self._compensation(data), raw=data,
            )

        title = _clean((soup.find("h1") or soup.find("h2") or {}).get_text(" ") if (soup.find("h1") or soup.find("h2")) else "")
        if not title:
            return None
        text = _clean(soup.get_text(" "))
        location = ""
        # Kula detail pages commonly render metadata as: Job type ... Department ... Work type ... Location
        # Keep fallback conservative; description still provides enough for scoring.
        m = re.search(r"(?:Work type:\s*[^·]+·?\s*)?([A-Za-z][A-Za-z .'-]+,\s*[A-Za-z .'-]+,\s*[A-Za-z .'-]+)", text)
        if m: location = _clean(m.group(1))
        return Job(
            company=company["name"], title=title, location=location, url=url,
            source="kula", source_id=source_id, description=text, raw={"html_fallback": True},
        )

    @staticmethod
    def _compensation(data: dict) -> str:
        sal = data.get("baseSalary")
        if not isinstance(sal, dict): return ""
        currency = sal.get("currency", "")
        value = sal.get("value", {})
        if not isinstance(value, dict): return ""
        lo, hi, unit = value.get("minValue"), value.get("maxValue"), value.get("unitText")
        if lo is None and hi is None: return ""
        rng = f"{lo}-{hi}" if lo is not None and hi is not None else str(lo if lo is not None else hi)
        return _clean(f"{currency} {rng} / {unit or ''}")
