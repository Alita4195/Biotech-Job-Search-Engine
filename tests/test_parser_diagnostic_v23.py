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
import pytest
pytestmark = pytest.mark.skip(reason="v2.4 isolates final two parser targets")
from pathlib import Path
import yaml
from biotech_jobs.adapters import ADAPTERS


def config():
    return yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())["companies"]

def test_v23_subset_and_routes():
    enabled=[c for c in config() if c.get("enabled")]
    assert len(enabled)==13
    d={c["name"]:c for c in enabled}
    assert d["Helix"]["platform"]=="gem" and d["Helix"]["board"]=="helix"
    assert d["Standard BioTools"]["platform"]=="workday" and d["Standard BioTools"]["board"]=="External"
    assert d["GeneDx"]["platform"]=="browser_career"
    assert d["Thermo Fisher Scientific"]["platform"]=="browser_career"
    assert d["Alnylam Pharmaceuticals"]["platform"]=="browser_career"
    assert d["Schrodinger"].get("heading_jobs") is True
    assert d["Persephone Biosciences"].get("zero_jobs_verified") is True
    assert "browser_career" in ADAPTERS
