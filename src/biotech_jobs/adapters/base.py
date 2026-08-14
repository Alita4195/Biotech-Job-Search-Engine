from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable
import requests
from biotech_jobs.models import Job


DEFAULT_DETAIL_TITLE_TERMS = (
    "bioinform", "computational", "genom", "genetic", "omics", "biomarker",
    "data scientist", "data science", "informatics", "algorithm", "machine learning",
    "applications scientist", "application scientist", "product owner", "scientific software",
    "systems biology", "biostat", "quantitative biology", "precision medicine",
)


class AdapterError(RuntimeError):
    pass


class BaseAdapter(ABC):
    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "biotech-job-engine/0.9 (+personal job discovery)"})

    def get_json(self, url: str, **kwargs):
        r = self.session.get(url, timeout=self.timeout, **kwargs)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def should_enrich_title(title: str, company: dict) -> bool:
        """Whether a listing deserves an extra detail-page request.

        Large ATS boards may contain hundreds of jobs. We preserve every board-level
        listing, but only spend another network request on titles plausibly relevant
        to this search profile. Terms can be overridden per company in YAML.
        """
        terms = company.get("detail_title_terms") or DEFAULT_DETAIL_TITLE_TERMS
        text = (title or "").lower()
        return any(str(term).lower() in text for term in terms)

    @abstractmethod
    def fetch(self, company: dict) -> Iterable[Job]: ...
