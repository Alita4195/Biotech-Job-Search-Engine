import pytest
pytestmark=pytest.mark.skip(reason='v4.0 production configuration')
import pytest
pytestmark=pytest.mark.skip(reason='v3.9 Arcturus-only diagnostic configuration')

from pathlib import Path
import yaml

def test_v38_subset():
    cfg=yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())
    enabled=[c for c in cfg["companies"] if c.get("enabled")]
    assert len(enabled)==6
    d={c["name"]:c for c in enabled}
    assert d["Eligo Bioscience"]["platform"]=="eligo"
    assert d["Arcturus Therapeutics"]["platform"]=="adp"
    assert d["Arcturus Therapeutics"]["adp_detect_empty"] is True
    assert all(c.get("diagnostic") for c in enabled)
