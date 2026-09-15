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
    def penalty(self): 
        return self.seniority_adjustment + self.other_penalty

    @property
    def total(self):
        # 加上了 location_fit，总分才完整
        raw = self.role_fit + self.domain_fit + self.technical_fit + self.operating_model_fit + self.leadership_fit + self.seniority_adjustment + self.other_penalty + self.location_fit
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
        # 极简模式：只更新总分、梯队、你的专属标识，删掉所有垃圾马甲
        d.update(
            total=self.total, 
            band=self.band, 
            scoring_version="job-v1",
            penalty=self.penalty
        )
        return d

# ... 此处保留原有的 _first_role_score 等中间辅助函数 ...

def score_job(job: Job) -> Score:
    p=load_profile()
    title=job.title or ""
    desc=job.description or ""
    meta=" ".join([job.department or "", job.team or ""])
    text=" ".join([title, desc, meta])
    
    # 彻底干掉地理位置加分，让总分100%反映专业契合度
    location_fit = 0
    
    other=_penalties(title,text,p.get("penalty_rules")) + _interaction_bonus(title,text,p.get("interaction_rules"))
    
    return Score(
        role_fit=_first_role_score(title,p.get("role_rules")),
        domain_fit=_category_score(text,p.get("domain_rules"),25),
        technical_fit=_category_score(text,p.get("technical_rules"),20),
        operating_model_fit=_category_score(text,p.get("operating_model_rules"),15),
        leadership_fit=_category_score(text,p.get("leadership_rules"),10),
        seniority_adjustment=_seniority_adjustment(title,p.get("seniority_rules")),
        other_penalty=other,
        location_fit=location_fit, # 永远为0
    )
