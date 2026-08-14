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
import pytest
pytestmark = pytest.mark.skip(reason='superseded by v2.3 parser diagnostic subset')

from pathlib import Path
import yaml

def test_v22_diagnostic_subset_and_routing():
    cfg=yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())
    enabled=[c for c in cfg["companies"] if c.get("enabled")]
    assert len(enabled)==26
    d={c["name"]:c for c in enabled}
    assert d["Viome"]["platform"]=="lever" and d["Viome"]["board"]=="viome"
    assert d["Color Health"]["platform"]=="ashby" and d["Color Health"]["board"]=="color-health"
    assert d["Akoya Biosciences"]["platform"]=="greenhouse" and d["Akoya Biosciences"]["board"]=="akoya"
    assert d["Quantum-Si"]["zero_result_verified"] is True
    assert d["Ferring Pharmaceuticals"].get("workday_seed_urls")
