from __future__ import annotations

import re
import html as _html
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional


@dataclass
class CompensationInfo:
    text: str = "Not listed"
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    currency: str = ""
    period: str = ""


def _html_to_text(value: str) -> str:
    """Convert ATS HTML fragments to readable text without losing pay-range separators."""
    value = value or ""
    if "<" in value and ">" in value:
        try:
            return BeautifulSoup(value, "html.parser").get_text(" ", strip=True)
        except Exception:
            pass
    return _html.unescape(value).replace("\xa0", " ")


def extract_greenhouse_pay_html(value: str) -> str:
    """Extract Greenhouse's dedicated pay-transparency range before HTML cleanup.

    Greenhouse commonly renders ranges as separate spans, e.g.
    ``<span>$166,600</span><span>—</span><span>$202,000 USD</span>``.
    Parsing this structurally avoids regex failures caused by intervening tags.
    """
    if not value:
        return ""
    try:
        soup = BeautifulSoup(value, "html.parser")
        node = soup.select_one(".content-pay-transparency .pay-range") or soup.select_one(".pay-range")
        if not node:
            return ""
        return node.get_text(" ", strip=True)
    except Exception:
        return ""


def _number(value: str) -> float:
    value = (value or "").strip().replace(",", "")
    mult = 1.0
    if value.lower().endswith("k"):
        mult = 1000.0
        value = value[:-1]
    return float(value) * mult


def _fmt_number(value: Optional[float]) -> str:
    if value is None:
        return ""
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def _normalize_period(value: str, minimum: Optional[float], maximum: Optional[float]) -> str:
    text = (value or "").lower().strip()
    if any(x in text for x in ("hour", "/hr", "per hr", "hourly")):
        return "hour"
    if any(x in text for x in ("year", "annual", "annum", "/yr", "yearly")):
        return "year"
    if any(x in text for x in ("month", "monthly")):
        return "month"
    # US biotech postings with five/six figure ranges are overwhelmingly annual.
    high = maximum if maximum is not None else minimum
    if high is not None:
        if high >= 1000:
            return "year"
        if high <= 1000:
            return "hour"
    return ""


def _currency(value: str) -> str:
    text = (value or "").upper()
    if "$" in value or "USD" in text or "US$" in text:
        return "USD"
    if "CAD" in text or "C$" in text:
        return "CAD"
    if "GBP" in text or "£" in value:
        return "GBP"
    if "EUR" in text or "€" in value:
        return "EUR"
    return ""


# Structured ATS strings such as "USD 150000-220000 year".
STRUCTURED_RANGE = re.compile(
    r"(?P<currency>USD|CAD|GBP|EUR|US\$|C\$|\$|£|€)?\s*"
    r"(?P<min>\d{2,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?[kK]?)\s*"
    r"(?:-|–|—|to)\s*"
    r"(?:(?:USD|CAD|GBP|EUR|US\$|C\$|\$|£|€)\s*)?"
    r"(?P<max>\d{2,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?[kK]?)"
    r"(?:\s*(?:USD|CAD|GBP|EUR))?"
    r"(?:\s*(?P<period>per\s+(?:year|hour|month)|/\s*(?:yr|year|hr|hour)|annual(?:ly)?|year(?:ly)?|hour(?:ly)?|month(?:ly)?))?",
    re.I,
)

# Compensation prose where the label supplies context and the currency appears only after the range,
# e.g. "Pay Range: 100,000 - 140,000 USD" (seen on Tempus Workday postings).
LABELED_RANGE = re.compile(
    r"(?:pay\s*range|salary\s*range|base\s*(?:pay|salary)|compensation(?:\s*range)?)\s*[:\-]?\s*"
    r"(?P<min>\d{2,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?[kK]?)\s*"
    r"(?:-|–|—|to)\s*"
    r"(?P<max>\d{2,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?[kK]?)"
    r"(?:\s*(?P<currency>USD|CAD|GBP|EUR))?"
    r"(?:\s*(?P<period>per\s+(?:year|hour|month)|/\s*(?:yr|year|hr|hour)|annual(?:ly)?|year(?:ly)?|hour(?:ly)?|month(?:ly)?))?",
    re.I,
)

# Public posting prose. Require a currency marker to avoid dates/years being mistaken for pay.
PROSE_RANGE = re.compile(
    r"(?P<currency>USD|CAD|GBP|EUR|US\$|C\$|\$|£|€)\s*"
    r"(?P<min>\d{2,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?[kK]?)\s*"
    r"(?:-|–|—|to)\s*"
    r"(?:(?:USD|CAD|GBP|EUR|US\$|C\$|\$|£|€)\s*)?"
    r"(?P<max>\d{2,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?[kK]?)"
    r"(?:\s*(?:USD|CAD|GBP|EUR))?"
    r"(?:\s*(?P<period>per\s+(?:year|hour|month)|/\s*(?:yr|year|hr|hour)|annual(?:ly)?|year(?:ly)?|hour(?:ly)?|month(?:ly)?))?",
    re.I,
)


def _parse_match(match: re.Match, source_text: str) -> CompensationInfo:
    minimum = _number(match.group("min"))
    maximum = _number(match.group("max"))
    if minimum > maximum:
        minimum, maximum = maximum, minimum
    currency = _currency(match.group("currency") or source_text)
    period = _normalize_period(match.groupdict().get("period") or "", minimum, maximum)
    symbol = "$" if currency == "USD" else (currency + " " if currency else "")
    if currency == "USD":
        display = f"${_fmt_number(minimum)}–${_fmt_number(maximum)}"
    else:
        display = f"{symbol}{_fmt_number(minimum)}–{symbol}{_fmt_number(maximum)}".strip()
    if period:
        display += f"/{'yr' if period == 'year' else 'hr' if period == 'hour' else 'mo'}"
    return CompensationInfo(display, minimum, maximum, currency, period)


def parse_compensation(raw: str = "", description: str = "") -> CompensationInfo:
    """Normalize published compensation, preferring structured ATS text.

    Never estimates pay. If the posting does not publish a recognizable range,
    returns ``Not listed`` with empty numeric metadata.
    """
    raw = (raw or "").strip()
    if raw and raw.lower() not in {"not listed", "n/a", "na", "none"}:
        m = STRUCTURED_RANGE.search(raw)
        if m:
            return _parse_match(m, raw)
        # Keep an explicit structured compensation string even if it cannot be normalized.
        if re.search(r"salary|compensation|pay|wage|\$|USD|CAD|GBP|EUR|£|€", raw, re.I):
            return CompensationInfo(text=raw, currency=_currency(raw))

    # Greenhouse may keep the pay range in separate HTML spans. Extract that first.
    html_pay = extract_greenhouse_pay_html(description or "")
    if html_pay:
        m = STRUCTURED_RANGE.search(_html_to_text(html_pay))
        if m:
            return _parse_match(m, html_pay)

    text = _html_to_text(description or "")

    # Some Workday postings omit a leading currency symbol but explicitly label the range.
    m = LABELED_RANGE.search(text)
    if m:
        minimum = _number(m.group("min")); maximum = _number(m.group("max"))
        if minimum > maximum:
            minimum, maximum = maximum, minimum
        currency = _currency(m.groupdict().get("currency") or text[m.start():m.end()+12]) or "USD"
        period = _normalize_period(m.groupdict().get("period") or "", minimum, maximum)
        display = f"${_fmt_number(minimum)}–${_fmt_number(maximum)}" if currency == "USD" else f"{currency} {_fmt_number(minimum)}–{_fmt_number(maximum)}"
        if period:
            display += f"/{'yr' if period == 'year' else 'hr' if period == 'hour' else 'mo'}"
        return CompensationInfo(display, minimum, maximum, currency, period)

    candidates = []
    for m in PROSE_RANGE.finditer(text):
        info = _parse_match(m, m.group(0))
        # Exclude implausible compensation ranges such as tiny incidental-dollar values.
        hi = info.maximum or 0
        if info.period == "year" and hi < 10000:
            continue
        if info.period == "hour" and hi < 10:
            continue
        # Prefer ranges close to compensation language when multiple dollar ranges exist.
        context = text[max(0, m.start()-180):min(len(text), m.end()+180)]
        priority = 0 if re.search(r"salary|compensation|pay range|wage|base pay|base salary|anticipated", context, re.I) else 1
        candidates.append((priority, m.start(), info))
    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1]))
        return candidates[0][2]
    return CompensationInfo()


def apply_compensation(job) -> None:
    info = parse_compensation(getattr(job, "compensation", ""), getattr(job, "description", ""))
    job.compensation = info.text
    job.compensation_min = info.minimum
    job.compensation_max = info.maximum
    job.compensation_currency = info.currency
    job.compensation_period = info.period
