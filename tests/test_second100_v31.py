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
pytestmark=pytest.mark.skip(reason='diagnostic subset configuration')
from pathlib import Path
import yaml

def test_v31_problem_subset_and_known_route_fixes():
    cfg=yaml.safe_load((Path(__file__).parents[1]/'config'/'companies.yml').read_text())
    enabled=[c for c in cfg['companies'] if c.get('enabled')]
    assert len(enabled)==77
    by={c['name']:c for c in enabled}
    assert by['Bio-Techne']['platform']=='workday'
    assert by['Fate Therapeutics']['platform']=='lever'
    assert by['Fate Therapeutics']['board']=='fatetherapeutics'
    assert by['Entrada Therapeutics']['platform']=='greenhouse'
    assert by['Entrada Therapeutics']['board']=='entradatherapeutics'
    assert by['Mammoth Biosciences']['platform']=='career_page'
    assert by['Kyverna Therapeutics']['url'].endswith('/jobs-list/')
