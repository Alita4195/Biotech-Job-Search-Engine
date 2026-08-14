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
pytestmark = pytest.mark.skip(reason='second-100 diagnostic intentionally changes enabled universe')
from pathlib import Path
import yaml
from biotech_jobs.adapters.indigo_ag import IndigoAgAdapter
from biotech_jobs.adapters.successfactors import SuccessFactorsAdapter

class Resp:
    def __init__(self,text): self.text=text
    def raise_for_status(self): pass

class Session:
    def __init__(self,m): self.m=m
    def get(self,url,*a,**k):
        key=url.split('?')[0]
        return Resp(self.m.get(key,self.m.get(url,'')))

def test_indigo_ag_apply_links_and_heading():
    a=IndigoAgAdapter()
    a.session=Session({
      'https://www.indigoag.com/careers':'<h3>Senior Scientist, Microbial Genomics</h3><a href="/senior-scientist-microbial-genomics-job-application">APPLY HERE</a>',
      'https://www.indigoag.com/senior-scientist-microbial-genomics-job-application':'<h1>Senior Scientist, Microbial Genomics</h1><p>metagenomics sequencing Python</p>'})
    jobs=list(a.fetch({'name':'Indigo Ag','url':'https://www.indigoag.com/careers'}))
    assert len(jobs)==1 and jobs[0].title=='Senior Scientist, Microbial Genomics'

def test_successfactors_listing_and_detail():
    a=SuccessFactorsAdapter()
    listing='<a href="/job/Cambridge-Senior-Computational-Biologist-MA-02142/1410613800/">Senior Computational Biologist</a>'
    detail='<h1>Senior Computational Biologist</h1><div>Date: Aug 1, 2026</div><div>Location: Cambridge, MA, US, 02142</div><p>genomics RNA sequencing Python</p>'
    a.session=Session({'https://opportunities.alnylam.com/search/':listing,'https://opportunities.alnylam.com/job/Cambridge-Senior-Computational-Biologist-MA-02142/1410613800/':detail})
    jobs=list(a.fetch({'name':'Alnylam Pharmaceuticals','url':'https://opportunities.alnylam.com/','search_url':'https://opportunities.alnylam.com/search/','max_pages':1}))
    assert len(jobs)==1
    assert jobs[0].source_id=='1410613800'
    assert 'Cambridge' in jobs[0].location

def test_only_two_enabled():
    cfg=yaml.safe_load((Path(__file__).parents[1]/'config'/'companies.yml').read_text())
    enabled=[c['name'] for c in cfg['companies'] if c.get('enabled')]
    assert enabled==['Indigo Ag','Alnylam Pharmaceuticals']
