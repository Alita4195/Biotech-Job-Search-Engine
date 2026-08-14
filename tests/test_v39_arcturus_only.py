import pytest
pytestmark=pytest.mark.skip(reason='v4.0 production configuration')

from pathlib import Path
import yaml

def test_v39_only_arcturus_enabled():
    cfg = yaml.safe_load((Path(__file__).parents[1] / "config" / "companies.yml").read_text())
    enabled = [c for c in cfg["companies"] if c.get("enabled")]
    assert len(enabled) == 1
    assert enabled[0]["name"] == "Arcturus Therapeutics"
    assert enabled[0]["platform"] == "adp"
    assert enabled[0]["adp_parse_rendered_cards"] is True
