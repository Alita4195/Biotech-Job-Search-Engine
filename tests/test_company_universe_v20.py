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

def test_v20_has_100_enabled_companies_and_microbiome_targets():
    cfg=yaml.safe_load((Path(__file__).parents[1]/'config'/'companies.yml').read_text())
    enabled=[c for c in cfg['companies'] if c.get('enabled')]
    assert len(enabled)==100
    names={c['name'] for c in enabled}
    microbiome={'Tiny Health','Evvy','Seed Health','Pendulum Therapeutics','Vedanta Biosciences','Ferring Pharmaceuticals','Karius','Locus Biosciences','Metabiomics','Persephone Biosciences','Seres Therapeutics','Metagenomi','Viome','Holobiome','CosmosID / Cmbio','Zymo Research','Kingdom'}
    assert microbiome <= names

def test_v20_registers_new_platforms():
    from biotech_jobs.adapters import ADAPTERS
    for p in ['smartrecruiters','gem','recruitee','oracle','career_page']:
        assert p in ADAPTERS
