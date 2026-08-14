from __future__ import annotations
from .base import BaseAdapter, AdapterError

class CustomAdapter(BaseAdapter):
    def fetch(self, company: dict):
        raise AdapterError(f"Custom collector not implemented for {company['name']}; configure a site-specific adapter.")
