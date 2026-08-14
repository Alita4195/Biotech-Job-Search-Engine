
from pathlib import Path
import yaml

def test_v40_production_universe():
    cfg=yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())
    d={c["name"]:c for c in cfg["companies"]}
    excluded={"Waters Corporation","Promega","Takara Bio USA","Eligo Bioscience","Deepcell"}
    for name in excluded:
        assert d[name]["enabled"] is False
    assert d["Arcturus Therapeutics"]["enabled"] is True
    assert d["Arcturus Therapeutics"]["platform"]=="adp"
    assert d["Arcturus Therapeutics"]["adp_parse_rendered_cards"] is True
    assert all(not c.get("diagnostic",False) for c in cfg["companies"])
    assert sum(bool(c.get("enabled")) for c in cfg["companies"]) > 100
