import time
import pytest
from biotech_jobs.engine import Engine, CompanyTimeoutError


class SlowAdapter:
    def fetch(self, company):
        time.sleep(2)
        return []


def test_hard_company_timeout(tmp_path):
    cfg = tmp_path / "companies.yml"
    cfg.write_text("companies: []\n")
    engine = Engine(cfg, tmp_path / "jobs.sqlite", company_timeout=1, request_timeout=1)
    if not hasattr(__import__('signal'), 'SIGALRM'):
        pytest.skip("SIGALRM unavailable on this platform")
    with pytest.raises(CompanyTimeoutError):
        engine._fetch_with_timeout(SlowAdapter(), {"name":"SlowCo"}, 1)
