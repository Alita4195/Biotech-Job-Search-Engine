
from .base import BaseAdapter

class EmptyAdapter(BaseAdapter):
    def fetch(self, company: dict):
        self.last_stats = {"pages": 0, "details_enriched": 0, "verified_empty": True}
        return iter(())
