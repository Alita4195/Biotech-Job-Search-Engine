from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Optional
import hashlib

@dataclass
class Job:
    company: str
    title: str
    location: str
    url: str
    source: str
    source_id: str
    description: str = ""
    department: str = ""
    team: str = ""
    workplace_type: str = ""
    employment_type: str = ""
    published_at: Optional[str] = None
    updated_at: Optional[str] = None
    compensation: str = ""
    compensation_min: Optional[float] = None
    compensation_max: Optional[float] = None
    compensation_currency: str = ""
    compensation_period: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def stable_key(self) -> str:
        basis = f"{self.company}|{self.source}|{self.source_id or self.url}".lower()
        return hashlib.sha256(basis.encode()).hexdigest()[:24]

    def to_dict(self):
        d = asdict(self)
        d.pop("raw", None)
        d["stable_key"] = self.stable_key
        return d
