
from urllib.parse import urljoin
import hashlib, re
from .base import BaseAdapter
from biotech_jobs.models import Job

EMPTY_RE = re.compile(
    r"(no jobs found|no open positions|no current openings|there are no jobs|current openings \(0 of 0\))",
    re.I
)
ROLE_RE = re.compile(
    r"\b(scientist|research associate|senior research associate|director|manager|engineer|"
    r"associate director|specialist|technician|analyst|developer|coordinator|clinical|"
    r"regulatory|quality|manufacturing|operations|finance|legal)\b", re.I
)
LOC_RE = re.compile(r"([A-Z][A-Za-z .'-]+,\s*[A-Z]{2},\s*US)")
META_PREFIX_RE = re.compile(
    r"^(?:\d+\s+(?:day|days|hour|hours|month|months)\s+ago)?"
    r"(?:Full Time|Part Time|Temporary|Contract)?\s*", re.I
)

class ADPAdapter(BaseAdapter):
    def fetch(self, company):
        from playwright.sync_api import sync_playwright
        url=company["url"]; found=[]; seen=set(); frames=0; rendered=""

        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page()
            page.goto(url,wait_until="domcontentloaded",
                      timeout=max(45000,self.timeout*1000))
            page.wait_for_timeout(int(company.get("render_wait_ms",6500)))
            for _ in range(5):
                try:
                    page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
                    page.wait_for_timeout(700)
                except Exception:
                    pass
            try:
                rendered=page.locator("body").inner_text()
            except Exception:
                rendered=""

            # Prefer structured DOM text around location nodes.
            try:
                body_text=" ".join(rendered.split())
            except Exception:
                body_text=""

            # Arcturus/ADP fallback: derive cards from location boundaries.
            if company.get("adp_parse_rendered_cards"):
                m=re.search(
                    r"Current Openings\s*\(\d+\s+of\s+\d+\)\s*(.*?)(?:Copyright|Privacy\s*\||$)",
                    body_text,re.I)
                section=m.group(1).strip() if m else body_text
                locs=list(LOC_RE.finditer(section))

                prev_end=0
                for i,lm in enumerate(locs):
                    raw=section[prev_end:lm.start()].strip()
                    location=lm.group(1).strip()

                    # Remove Search at start of first card.
                    raw=re.sub(r"^Search\s+","",raw,flags=re.I)

                    # Remove previous card metadata at the beginning of subsequent chunks.
                    raw=META_PREFIX_RE.sub("",raw).strip()

                    # If metadata is glued to next title (e.g. "19 days agoTemporary Director"),
                    # strip it while preserving the following title.
                    raw=re.sub(
                        r"^\d+\s+(?:day|days|hour|hours|month|months)\s+ago\s*",
                        "",raw,flags=re.I)
                    raw=re.sub(r"^(?:Full Time|Part Time|Temporary|Contract)\s+",
                               "",raw,flags=re.I)

                    title=raw.strip(" -|")
                    if ROLE_RE.search(title) and 3 < len(title) < 220:
                        synthetic=url+"#job-"+hashlib.sha1(
                            (title+"|"+location).encode()).hexdigest()[:12]
                        if synthetic not in seen:
                            seen.add(synthetic)
                            found.append((title,location,synthetic))

                    # The text after this location up to the next title contains age/employment.
                    # Advance to immediately after this location; next iteration strips metadata.
                    prev_end=lm.end()

            # Anchor fallback for other ADP boards.
            if not found:
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
                        if full in seen or not label: continue
                        navish=any(x in low for x in (
                            "privacy","support","login","home","search jobs","view all","career center"))
                        if "workforcenow.adp.com" in full and ROLE_RE.search(label) and not navish:
                            seen.add(full); found.append((label,"",full))
            browser.close()

        verified_empty=bool(company.get("adp_detect_empty") and EMPTY_RE.search(rendered or ""))
        self.last_stats={
            "pages":1,"details_enriched":0,"links_discovered":len(found),
            "frames":frames,"verified_empty":verified_empty
        }
        for title,location,href in found:
            yield Job(
                company=company["name"],title=title,location=location,url=href,
                source="adp",source_id=hashlib.sha1(href.encode()).hexdigest()[:20],
                description="",raw={"board_url":url})
