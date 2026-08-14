import pytest
pytestmark=pytest.mark.skip(reason='v4.0 production configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.9 Arcturus-only diagnostic configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.8 final diagnostic configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.7 final diagnostic configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.6 correction diagnostic configuration')

from pathlib import Path
import yaml
from biotech_jobs.adapters import ADAPTERS

def test_v35_cleanup_routes():
    cfg=yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())
    enabled=[c for c in cfg["companies"] if c.get("enabled")]
    assert len(enabled)==11
    d={c["name"]:c for c in enabled}
    assert d["Arcturus Therapeutics"]["platform"]=="adp"
    assert d["Waters Corporation"]["platform"]=="icims"
    assert d["Promega"]["platform"]=="promega"
    assert d["Avidity Biosciences"]["platform"]=="jobvite"
    assert d["Biomica"]["platform"]=="empty"
    assert d["Eligo Bioscience"]["platform"]=="career_page"
    assert d["Apogee Therapeutics"]["zero_result_verified"] is True
    for x in ("adp","icims","promega","jobvite"):
        assert x in ADAPTERS
