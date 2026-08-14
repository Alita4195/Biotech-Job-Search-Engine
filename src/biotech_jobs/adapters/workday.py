from __future__ import annotations
from typing import Iterable
import json
from urllib.parse import urljoin, urlparse
import re
import time
from bs4 import BeautifulSoup
from .base import BaseAdapter, AdapterError
from biotech_jobs.models import Job


class WorkdayAdapter(BaseAdapter):
    """Retrieve public postings from a configured Workday CXS career site.

    v0.7 deliberately separates board pagination from detail enrichment. Board
    retrieval continues until an empty/duplicate page (or max_pages), regardless
    of Workday's sometimes-inconsistent `total` value. Full descriptions remain
    capped to plausible titles for performance.
    """

    def _validate(self, company: dict):
        missing = [k for k in ("host", "tenant", "board") if not company.get(k)]
        if missing:
            raise AdapterError(
                f"Workday adapter for {company.get('name','company')} missing config: {', '.join(missing)}"
            )

    def _variants(self, company: dict):
        """Configured primary endpoint plus optional fallbacks for tenant/site migrations."""
        primary = {"host": company["host"], "tenant": company["tenant"], "board": company["board"]}
        yield primary
        for v in company.get("workday_fallbacks", []) or []:
            merged = dict(primary); merged.update(v or {})
            if merged != primary:
                yield merged

    @staticmethod
    def _cxs_base_variant(v: dict) -> str:
        return f"https://{v['host']}/wday/cxs/{v['tenant']}/{v['board']}"

    @staticmethod
    def _public_base_variant(v: dict, locale: str) -> str:
        return f"https://{v['host']}/{locale}/{v['board']}"

    def _post_json(self, url: str, payload: dict, *, timeout: int | None = None, retries: int = 0):
        """POST a Workday board request with small, bounded retries.

        Board requests are more important than detail enrichment and some Workday
        tenants occasionally respond slowly or transiently fail.  Retries are
        intentionally bounded so the engine-level company timeout still wins.
        """
        timeout = timeout or self.timeout
        last_exc = None
        for attempt in range(retries + 1):
            try:
                r = self.session.post(
                    url, json=payload, timeout=timeout,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                )
                r.raise_for_status()
                return r.json()
            except Exception as exc:
                last_exc = exc
                if attempt >= retries:
                    raise
                time.sleep(min(1.5 * (attempt + 1), 3.0))
        raise last_exc

    def _discover_variants(self, company: dict):
        """Best-effort discovery of tenant/board metadata from public Workday HTML.

        This is a fallback for companies whose visible careers URL is current but
        whose CXS tenant identifier differs from the obvious hostname prefix.
        """
        locale = company.get("locale", "en-US")
        seeds = list(company.get("workday_seed_urls", []) or [])
        seeds.append(f"https://{company['host']}/{locale}/{company['board']}")
        seen = set()
        patterns = (
            re.compile(r"/wday/cxs/([^/\"']+)/([^/\"'?]+)"),
            re.compile(r"wday/cxs/([^/\"']+)/([^/\"'?]+)"),
        )
        for seed in seeds:
            try:
                r = self.session.get(seed, timeout=company.get("discovery_timeout", self.timeout))
                r.raise_for_status()
                text = getattr(r, "text", "") or ""
            except Exception:
                continue
            for pat in patterns:
                for tenant, board in pat.findall(text):
                    key = (tenant, board)
                    if key in seen:
                        continue
                    seen.add(key)
                    yield {"host": company["host"], "tenant": tenant, "board": board}

    def _detail(self, base: str, external_path: str) -> dict:
        if not external_path:
            return {}
        return self.get_json(base + external_path)

    @staticmethod
    def _clean_html(value: str) -> str:
        if not value:
            return ""
        return BeautifulSoup(value, "html.parser").get_text(" ", strip=True)

    @staticmethod
    def _compensation(info: dict) -> str:
        for key in ("compensation", "salary", "salaryRange", "payRange"):
            value = info.get(key)
            if isinstance(value, str) and value.strip(): return value.strip()
            if isinstance(value, dict):
                vals = [str(value.get(k, "")).strip() for k in ("currency", "min", "max", "interval")]
                txt = " ".join(v for v in vals if v)
                if txt: return txt
        return ""

    @staticmethod
    def _location_is_malformed(value) -> bool:
        """Detect common Workday location payload failures (e.g. numeric facet IDs)."""
        text = str(value or "").strip()
        if not text:
            return True
        if re.fullmatch(r"[\d.,;:+_-]+", text):
            return True
        if len(text) <= 2 and not re.search(r"[A-Za-z]{2}", text):
            return True
        return False

    @staticmethod
    def _location_from_external_path(external_path: str) -> str:
        """Recover a human-readable location from Workday's public job URL path."""
        path = str(external_path or "")
        m = re.search(r"/job/([^/]+)/[^/]+$", path)
        if not m:
            return ""
        segment = m.group(1).strip()
        # Only treat the segment as a location when Workday encoded one there.
        if not re.search(r"(?:US|United[- ]States|Remote|CA|California)", segment, re.I):
            return ""
        text = segment.replace("---", " - ").replace("--", " - ").replace("_", " ")
        text = re.sub(r"(?<!\s)-(?!\s)", " ", text)
        text = re.sub(r"\s+", " ", text).strip(" -")
        return text

    @classmethod
    def _normalize_location(cls, value, external_path: str = "", description: str = "") -> str:
        """Prefer ATS location, but repair malformed values from URL/description evidence."""
        text = str(value or "").strip()
        if not cls._location_is_malformed(text):
            return text
        recovered = cls._location_from_external_path(external_path)
        if recovered:
            return recovered
        desc = str(description or "")[:1800]
        patterns = (
            r"located in\s+((?:US|United States)\s*-\s*[A-Z]{2}\s*-\s*[A-Za-z .-]+)",
            r"locations?\s+((?:US|United States)\s*-\s*[A-Z]{2}\s*-\s*[A-Za-z .-]+)",
            r"\b(US\s*-\s*Remote)\b",
        )
        for pat in patterns:
            m = re.search(pat, desc, re.I)
            if m:
                return re.sub(r"\s+", " ", m.group(1)).strip(" .")
        return "" if cls._location_is_malformed(text) else text

    def _fetch_variant(self, company: dict, v: dict) -> list[Job]:
        locale = company.get("locale", "en-US")
        cxs_base = self._cxs_base_variant(v)
        public_base = self._public_base_variant(v, locale)
        jobs_url = cxs_base + "/jobs"
        page_size = min(max(int(company.get("page_size", 20)), 1), 20)
        max_pages = int(company.get("max_pages", 200))
        detail_budget = int(company.get("max_detail_requests", 40))
        board_timeout = int(company.get("board_request_timeout", max(self.timeout, 18)))
        board_retries = int(company.get("board_retries", 1))
        detail_count = 0
        offset = 0
        seen_paths = set()
        out = []
        pages = 0

        for _ in range(max_pages):
            pages += 1
            payload = {"appliedFacets": {}, "limit": page_size, "offset": offset, "searchText": ""}
            data = self._post_json(jobs_url, payload, timeout=board_timeout, retries=board_retries)
            postings = data.get("jobPostings") or []
            if not postings:
                break

            new_on_page = 0
            for listing in postings:
                external_path = listing.get("externalPath", "") or ""
                # Workday can occasionally repeat the last page. Stop counting duplicates.
                dedupe_key = external_path or f"{listing.get('title','')}|{listing.get('locationsText','')}"
                if dedupe_key in seen_paths:
                    continue
                seen_paths.add(dedupe_key); new_on_page += 1

                listing_title = listing.get("title", "") or ""
                detail = {}
                if detail_count < detail_budget and self.should_enrich_title(listing_title, company):
                    try:
                        detail = self._detail(cxs_base, external_path)
                        detail_count += 1
                    except Exception:
                        detail = {}
                info = detail.get("jobPostingInfo") or detail.get("jobPosting") or detail

                description = self._clean_html(
                    info.get("jobDescription") or info.get("description") or listing.get("jobDescription") or ""
                )
                raw_location = info.get("location") or info.get("locationsText") or listing.get("locationsText") or listing.get("location") or ""
                location = self._normalize_location(raw_location, external_path, description)
                bullets = listing.get("bulletFields") or []
                source_id = str(info.get("jobReqId") or info.get("jobRequisitionId") or (bullets[0] if bullets else "") or external_path)
                out.append(Job(
                    company=company["name"], title=info.get("title") or listing_title,
                    location=location, url=public_base + external_path,
                    source="workday", source_id=source_id, description=description,
                    department=info.get("department", "") or "", team=info.get("team", "") or "",
                    workplace_type=info.get("workplaceType", "") or "",
                    employment_type=info.get("timeType", "") or info.get("employmentType", "") or "",
                    published_at=info.get("startDate") or info.get("postedOn") or listing.get("postedOn"),
                    updated_at=info.get("updatedAt"), compensation=self._compensation(info),
                    raw={"listing": listing, "detail": detail},
                ))

            if new_on_page == 0:
                break
            offset += len(postings)
            if len(postings) < page_size:
                break
        self.last_stats = {"pages": pages, "board_jobs": len(out), "details_enriched": detail_count}
        return out

    @staticmethod
    def _jsonld_job_from_html(html: str) -> dict:
        soup = BeautifulSoup(html or "", "html.parser")
        for node in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                data = json.loads(node.get_text(strip=True) or "{}")
            except Exception:
                continue
            candidates = data if isinstance(data, list) else [data]
            for item in candidates:
                if isinstance(item, dict) and item.get("@type") == "JobPosting":
                    return item
                if isinstance(item, dict) and isinstance(item.get("@graph"), list):
                    for child in item["@graph"]:
                        if isinstance(child, dict) and child.get("@type") == "JobPosting":
                            return child
        return {}

    @staticmethod
    def _schema_location(data: dict) -> str:
        loc = data.get("jobLocation") or data.get("applicantLocationRequirements") or ""
        if isinstance(loc, list):
            vals = [WorkdayAdapter._schema_location({"jobLocation": x}) for x in loc]
            return "; ".join(v for v in vals if v)
        if isinstance(loc, dict):
            addr = loc.get("address") or loc
            if isinstance(addr, dict):
                parts = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
                return ", ".join(str(x) for x in parts if x)
            return str(loc.get("name") or "")
        return str(loc or "")

    @staticmethod
    def _seed_spec(item):
        if isinstance(item, str):
            return {"url": item}
        if isinstance(item, dict):
            return dict(item)
        return {}

    @staticmethod
    def _title_from_job_url(url: str) -> str:
        path = urlparse(url).path
        slug = path.rstrip("/").split("/")[-1] if path else ""
        slug = re.sub(r"_((?:R|JR)\d+[A-Za-z0-9-]*)$", "", slug, flags=re.I)
        return re.sub(r"[-_]+", " ", slug).strip()

    def _seeded_public_fallback(self, company: dict) -> list[Job]:
        """Recover configured Workday job pages after CXS board failure.

        Workday often returns a JavaScript application shell with no JSON-LD to a
        plain HTTP client. v1.0 therefore allows a seed to carry verified title,
        location and a short search-oriented description. Seed metadata is used
        only when the public URL returns successfully; HTTP failures/404s are not
        turned into jobs. Same-host /job/ links are still crawled opportunistically.
        """
        if not company.get("public_seed_fallback"):
            return []
        seed_specs = [self._seed_spec(x) for x in (company.get("workday_seed_urls", []) or [])]
        seed_specs = [x for x in seed_specs if x.get("url")]
        max_pages = int(company.get("public_seed_max_pages", 25))
        queue = list(seed_specs)
        visited, out, seen_ids = set(), [], set()
        host = company.get("host", "")

        while queue and len(visited) < max_pages:
            spec = queue.pop(0)
            url = spec.get("url", "")
            if not url or url in visited:
                continue
            visited.add(url)
            try:
                r = self.session.get(url, timeout=company.get("discovery_timeout", self.timeout))
                r.raise_for_status()
                html = getattr(r, "text", "") or ""
            except Exception:
                continue

            data = self._jsonld_job_from_html(html)
            soup = BeautifulSoup(html, "html.parser")
            title = str(data.get("title") or spec.get("title") or "").strip()
            if not title:
                h = soup.find(["h1", "h2"])
                title = h.get_text(" ", strip=True) if h else self._title_from_job_url(url)
            desc = self._clean_html(data.get("description") or spec.get("description") or "")
            location = self._schema_location(data) or str(spec.get("location") or "")
            location = self._normalize_location(location, urlparse(url).path, desc)
            source_id = str(data.get("identifier", ""))
            if isinstance(data.get("identifier"), dict):
                source_id = str(data["identifier"].get("value") or "")
            if not source_id:
                m = re.search(r"_((?:R|JR)\d+[A-Za-z0-9-]*)", url, re.I)
                source_id = m.group(1) if m else url

            if title and "/job/" in url and source_id not in seen_ids:
                seen_ids.add(source_id)
                out.append(Job(
                    company=company["name"], title=title, location=location, url=url,
                    source="workday-public", source_id=source_id, description=desc,
                    employment_type=str(data.get("employmentType") or spec.get("employment_type") or ""),
                    published_at=str(data.get("datePosted") or spec.get("published_at") or "") or None,
                    raw={"jsonld": data, "seed_metadata_used": bool(spec)},
                ))

            # Crawl bounded same-host Workday job links exposed by a server-rendered page.
            for a in soup.find_all("a", href=True):
                href = urljoin(url, a.get("href"))
                if host and urlparse(href).netloc != host:
                    continue
                if "/job/" in href and href not in visited and all(q.get("url") != href for q in queue):
                    queue.append({"url": href})

        self.last_stats = {"pages": len(visited), "board_jobs": len(out), "details_enriched": len(out), "fallback": "public-seed"}
        return out

    def fetch(self, company: dict) -> Iterable[Job]:
        self._validate(company)
        errors = []
        tried = set()

        def attempt(v):
            key = (v.get("host"), v.get("tenant"), v.get("board"))
            if key in tried:
                return None
            tried.add(key)
            try:
                jobs = self._fetch_variant(company, v)
                if jobs:
                    return jobs
                errors.append(f"{v['tenant']}/{v['board']}: zero jobs")
            except Exception as e:
                errors.append(f"{v['tenant']}/{v['board']}: {type(e).__name__}: {e}")
            return None

        for v in self._variants(company):
            jobs = attempt(v)
            if jobs:
                return jobs

        # If configured CXS identifiers fail, inspect the public careers HTML for
        # embedded CXS metadata and try any identities discovered there.
        for v in self._discover_variants(company):
            jobs = attempt(v)
            if jobs:
                return jobs

        fallback_jobs = self._seeded_public_fallback(company)
        if fallback_jobs:
            return fallback_jobs

        raise AdapterError("Workday endpoint variants failed: " + " | ".join(errors))
