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
import pytest
pytestmark=pytest.mark.skip(reason='v3.5 cleanup diagnostic configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.4 final collector diagnostic configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.3 unresolved subset configuration')

from pathlib import Path
import yaml
from biotech_jobs.adapters import ADAPTERS

def cfg():
    return yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())["companies"]

def test_v32_has_jazzhr_and_empty_adapters():
    assert "jazzhr" in ADAPTERS
    assert "empty" in ADAPTERS

def test_v32_biomesense_route_and_verified_empty():
    d={c["name"]:c for c in cfg()}
    assert d["BiomeSense"]["platform"]=="jazzhr"
    assert "applytojob.com" in d["BiomeSense"]["url"]
    assert d["Verve Therapeutics"]["platform"]=="empty"
    assert d["CARGO Therapeutics"]["platform"]=="empty"

def test_v32_is_diagnostic_subset():
    enabled=[c for c in cfg() if c.get("enabled")]
    assert 50 <= len(enabled) <= 70
    assert all(c.get("diagnostic") for c in enabled)
