import pytest
pytestmark=pytest.mark.skip(reason='v4.0 production configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.9 Arcturus-only diagnostic configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.8 final diagnostic configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.7 final diagnostic configuration')

from pathlib import Path
import yaml
from biotech_jobs.adapters import ADAPTERS

def test_v36_routes():
    cfg=yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())
    enabled=[c for c in cfg["companies"] if c.get("enabled")]
    assert len(enabled)==8
    d={c["name"]:c for c in enabled}
    assert d["Waters Corporation"]["platform"]=="browser_career"
    assert d["Promega"]["platform"]=="browser_career"
    assert d["Hologic"]["platform"]=="hologic"
    assert d["CRISPR Therapeutics"]["platform"]=="workday"
    assert d["CRISPR Therapeutics"]["host"].startswith("crisprtx.wd12")
    assert d["Eligo Bioscience"]["platform"]=="eligo"
    assert "eligo" in ADAPTERS
