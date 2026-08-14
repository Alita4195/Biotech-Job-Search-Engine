from __future__ import annotations
import os, re
from pathlib import Path
from dataclasses import dataclass, asdict
import yaml
from biotech_jobs.models import Job

PROFILE_PATH = Path(os.getenv("BIOTECH_JOB_PROFILE", "config/search_profile.yml"))
_PROFILE = None


def load_profile(force=False):
    global _PROFILE
    if _PROFILE is None or force:
        if not PROFILE_PATH.exists():
            raise FileNotFoundError(f"Scoring profile not found: {PROFILE_PATH}")
        _PROFILE = yaml.safe_load(PROFILE_PATH.read_text()) or {}
    return _PROFILE


def _search(pattern, text):
    try:
        return re.search(pattern, text or "", re.I) is not None
    except re.error as e:
        raise ValueError(f"Invalid regex in {PROFILE_PATH}: {pattern!r}: {e}") from e


def _any(patterns, text):
    return any(_search(p, text) for p in (patterns or []))


@dataclass
class Score:
    role_fit: int = 0
    domain_fit: int = 0
    technical_fit: int = 0
    operating_model_fit: int = 0
    leadership_fit: int = 0
    seniority_adjustment: int = 0
    other_penalty: int = 0
    location_fit: int = 0

    @property
    def function(self): return self.role_fit
    @property
    def genomics(self): return min(15, self.domain_fit)
    @property
    def technical(self): return min(15, self.technical_fit)
    @property
    def domain(self): return min(15, self.domain_fit)
    @property
    def product_workflow(self): return min(10, self.operating_model_fit)
    @property
    def seniority(self): return 10 if self.seniority_adjustment == 0 else 0
    @property
    def leadership(self): return min(5, self.leadership_fit)
    @property
    def industry(self): return 0
    @property
    def penalty(self): return self.seniority_adjustment + self.other_penalty
    @property
    def total(self):
        raw = self.role_fit + self.domain_fit + self.technical_fit + self.operating_model_fit + self.leadership_fit + self.seniority_adjustment + self.other_penalty
        return max(0, min(100, raw))
    @property
    def band(self):
        p=load_profile(); bands=p.get("score_bands", {})
        if self.total >= int(bands.get("exceptional",85)): return "Exceptional"
        if self.total >= int(bands.get("strong",75)): return "Strong"
        if self.total >= int(bands.get("review",65)): return "Review"
        return "Lower Fit"
    def to_dict(self):
        d=asdict(self)
        d.update(total=self.total, band=self.band, scoring_version="profile-v1",
                 function=self.function, genomics=self.genomics, technical=self.technical,
                 domain=self.domain, product_workflow=self.product_workflow,
                 seniority=self.seniority, leadership=self.leadership,
                 industry=self.industry, penalty=self.penalty)
        return d


def _first_role_score(title, rules):
    for rule in rules or []:
        if _any(rule.get("patterns"), title):
            return int(rule.get("score",0))
    return 0


def _category_score(text, rules, cap):
    score=0
    for rule in rules or []:
        if _any(rule.get("patterns"), text):
            score += int(rule.get("weight",0))
    return min(cap, score)


def _seniority_adjustment(title, rules):
    for rule in rules or []:
        if _any(rule.get("patterns"), title):
            return int(rule.get("adjustment",0))
    return 0


def _penalties(title, text, rules):
    total=0
    for rule in rules or []:
        title_hit = _any(rule.get("title_patterns"), title) if rule.get("title_patterns") else True
        text_hit = _any(rule.get("text_patterns"), text) if rule.get("text_patterns") else True
        unless_title = _any(rule.get("unless_title_patterns"), title)
        unless_text = _any(rule.get("unless_text_patterns"), text)
        if title_hit and text_hit and not unless_title and not unless_text:
            total += int(rule.get("adjustment",0))
    return total


def _interaction_bonus(title, text, rules):
    total=0
    for rule in rules or []:
        all_title = all(_any(group, title) for group in rule.get("all_title_pattern_groups", []))
        all_text = all(_any(group, text) for group in rule.get("all_text_pattern_groups", []))
        title_ok = all_title if rule.get("all_title_pattern_groups") else True
        text_ok = all_text if rule.get("all_text_pattern_groups") else True
        if title_ok and text_ok:
            total += int(rule.get("bonus",0))
    return total


def alert_location_eligible(job: Job) -> bool:
    p=load_profile().get("location", {})
    if not p.get("enabled", True): return True
    loc=f"{job.location or ''} {job.workplace_type or ''}".strip().lower()
    url=(job.url or "").lower()
    if not loc and not url: return bool(p.get("allow_ambiguous", True))
    if _any(p.get("allowed_patterns"), loc): return True
    if _any(p.get("excluded_patterns"), loc): return False
    if _any(p.get("excluded_patterns"), url): return False
    if _any(p.get("allowed_patterns"), url): return True
    return bool(p.get("allow_ambiguous", True))


def score_job(job: Job) -> Score:
    p=load_profile()
    title=job.title or ""
    desc=job.description or ""
    meta=" ".join([job.department or "", job.team or ""])
    text=" ".join([title, desc, meta])
    loc=f"{job.location or ''} {job.workplace_type or ''}".lower()
    location_fit=5 if ("remote" in loc or "san diego" in loc or "la jolla" in loc) else (3 if "california" in loc else 0)
    other=_penalties(title,text,p.get("penalty_rules")) + _interaction_bonus(title,text,p.get("interaction_rules"))
    return Score(
        role_fit=_first_role_score(title,p.get("role_rules")),
        domain_fit=_category_score(text,p.get("domain_rules"),25),
        technical_fit=_category_score(text,p.get("technical_rules"),20),
        operating_model_fit=_category_score(text,p.get("operating_model_rules"),15),
        leadership_fit=_category_score(text,p.get("leadership_rules"),10),
        seniority_adjustment=_seniority_adjustment(title,p.get("seniority_rules")),
        other_penalty=other,
        location_fit=location_fit,
    )
