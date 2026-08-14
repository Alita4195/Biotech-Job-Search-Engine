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

from pathlib import Path
import yaml

def test_v33_unresolved_subset():
    cfg=yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())
    enabled=[c for c in cfg["companies"] if c.get("enabled")]
    assert len(enabled)==33
    d={c["name"]:c for c in enabled}
    assert d["Waters Corporation"]["url"].startswith("https://internationalcareers-waters.icims.com")
    assert d["Pattern Bioscience"]["platform"]=="lever"
    assert d["MaaT Pharma"]["url"].endswith("/job-offers/")
    assert d["Adaptive Phage Therapeutics"]["platform"]=="empty"
    assert d["Capstan Therapeutics"]["platform"]=="empty"
