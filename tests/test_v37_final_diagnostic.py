import pytest
pytestmark=pytest.mark.skip(reason='v4.0 production configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.9 Arcturus-only diagnostic configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.8 final diagnostic configuration')

from pathlib import Path
import yaml
from biotech_jobs.adapters import ADAPTERS

def test_v37_subset():
    cfg=yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())
    enabled=[c for c in cfg["companies"] if c.get("enabled")]
    assert len(enabled)==6
    names={c["name"] for c in enabled}
    assert names=={"Waters Corporation","Promega","Takara Bio USA","Eligo Bioscience",
                   "Arcturus Therapeutics","Deepcell"}
    d={c["name"]:c for c in enabled}
    assert d["Eligo Bioscience"]["platform"]=="eligo"
    assert d["Arcturus Therapeutics"]["platform"]=="adp"
    assert "eligo" in ADAPTERS and "adp" in ADAPTERS
