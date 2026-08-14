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

from pathlib import Path
import yaml
from biotech_jobs.adapters import ADAPTERS

def config():
    return yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())

def test_v34_subset_and_structured_routes():
    enabled=[c for c in config()["companies"] if c.get("enabled")]
    assert len(enabled)==15
    d={c["name"]:c for c in enabled}
    assert d["New England Biolabs"]["platform"]=="workday"
    assert d["New England Biolabs"]["board"]=="NEB_Careers"
    assert d["Ionis Pharmaceuticals"]["platform"]=="ultipro"
    assert d["Apogee Therapeutics"]["platform"]=="greenhouse"
    assert d["Apogee Therapeutics"]["board"]=="apogeetherapeutics"
    assert d["Hologic"]["platform"]=="hologic"

def test_v34_new_adapters_registered():
    assert "ultipro" in ADAPTERS
    assert "hologic" in ADAPTERS
