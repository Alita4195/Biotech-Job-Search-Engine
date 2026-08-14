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
pytestmark = pytest.mark.skip(reason='diagnostic subset intentionally enables only problematic companies')
from pathlib import Path
import yaml

def test_v15_company_universe():
    cfg = yaml.safe_load((Path(__file__).parents[1] / "config" / "companies.yml").read_text())
    enabled = [c for c in cfg["companies"] if c.get("enabled")]
    names = {c["name"] for c in enabled}
    expected = {
        "Singular Genomics","Ultima Genomics","Freenome","Personalis","BillionToOne",
        "Parse Biosciences","Quantum-Si","CareDx","Fabric Genomics","Boundless Bio"
    }
    assert len(enabled) >= 34
    assert expected <= names
    for c in enabled:
        if c["name"] in expected:
            assert c["platform"] == "greenhouse"
            assert c.get("board")
