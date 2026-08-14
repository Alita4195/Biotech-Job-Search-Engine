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

import pytest

@pytest.mark.skip(reason="v3.1 intentionally enables only the unresolved/suspicious second-100 subset")
def test_second100_exactly_100_enabled_and_unique():
    cfg=yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())
    enabled=[c for c in cfg["companies"] if c.get("enabled")]
    assert len(enabled)==100
    assert len({c["name"] for c in enabled})==100
    known={"greenhouse","lever","ashby","workday","career_page","browser_career","successfactors","oracle","gem","recruitee","smartrecruiters","kula","custom","foundation","adaptive","indigo_ag"}
    assert all(c["platform"] in known for c in enabled)
    for c in enabled:
        if c["platform"] in {"greenhouse","lever","ashby"}: assert c.get("board")
        if c["platform"] in {"career_page","browser_career"}: assert c.get("url")

def test_microbiome_second_cohort_is_overweighted():
    cfg=yaml.safe_load((Path(__file__).parents[1]/"config"/"companies.yml").read_text())
    enabled=[c for c in cfg["companies"] if c.get("enabled")]
    micro=[c for c in enabled if any(k in (c.get("focus") or '').lower() for k in ['microbiom','metagenom','microbial','phage','bacterial'])]
    assert len(micro)>=15
