from biotech_jobs.adapters.smartrecruiters import SmartRecruitersAdapter
from biotech_jobs.adapters.gem import GemAdapter
from biotech_jobs.adapters.recruitee import RecruiteeAdapter
from biotech_jobs.adapters.oracle import OracleAdapter
from biotech_jobs.adapters.career_page import CareerPageAdapter

class Resp:
    def __init__(self, text='', data=None, status=200): self.text=text; self._data=data; self.status_code=status
    def raise_for_status(self):
        if self.status_code >= 400: raise RuntimeError(self.status_code)
    def json(self): return self._data

class Session:
    def __init__(self, mapping): self.mapping=mapping
    def get(self, url, **kwargs):
        item=self.mapping.get(url)
        if item is None:
            # oracle page with query params still uses same URL key
            item=self.mapping.get(url.split('?')[0])
        return item

def test_smartrecruiters_normalization(monkeypatch):
    a=SmartRecruitersAdapter()
    def gj(url, params=None):
        if url.endswith('/postings'):
            return {'content':[{'uuid':'abc','name':'Senior Bioinformatics Scientist','location':{'city':'San Diego','region':'CA','country':'US'},'ref':'https://x/job'}], 'totalFound':1}
        return {'uuid':'abc','name':'Senior Bioinformatics Scientist','location':{'city':'San Diego','region':'CA','country':'US'}, 'ref':'https://x/job','jobAd':{'sections':{'jobDescription':{'text':'NGS genomics Python'}}}}
    monkeypatch.setattr(a,'get_json',gj)
    jobs=list(a.fetch({'name':'DNAnexus','board':'DNAnexus'}))
    assert len(jobs)==1 and jobs[0].title=='Senior Bioinformatics Scientist' and 'San Diego' in jobs[0].location

def test_gem_normalization(monkeypatch):
    a=GemAdapter()
    monkeypatch.setattr(a,'get_json',lambda url:{'job_posts':[{'id':'1','title':'Computational Biologist','locations':[{'name':'Remote - US'}],'job_post_url':'https://x/1','description':'genomics'}]})
    j=list(a.fetch({'name':'Helix','board':'helix'}))[0]
    assert j.title=='Computational Biologist' and 'Remote' in j.location

def test_recruitee_public_offers(monkeypatch):
    a=RecruiteeAdapter()
    monkeypatch.setattr(a,'get_json',lambda url:{'offers':[{'id':2,'status':'published','title':'Scientist, Microbiome','slug':'microbiome','locations':[{'name':'Morrisville, NC'}],'description':'<p>metagenomics</p>'}]})
    j=list(a.fetch({'name':'Locus Biosciences','board':'locusbiosciences'}))[0]
    assert 'Microbiome' in j.title and j.description=='metagenomics'

def test_oracle_server_rendered_jsonld():
    base='https://oracle.example/jobs'
    detail='https://oracle.example/job/123'
    listing=f'<html><a href="/job/123">Bioinformatics Scientist</a></html>'
    job='''<script type="application/ld+json">{"@type":"JobPosting","title":"Bioinformatics Scientist","url":"https://oracle.example/job/123","identifier":{"value":"123"},"jobLocation":{"address":{"addressLocality":"San Diego","addressRegion":"CA","addressCountry":"US"}},"description":"NGS genomics"}</script>'''
    a=OracleAdapter(); a.session=Session({base:Resp(listing),detail:Resp(job)})
    jobs=list(a.fetch({'name':'Oxford Nanopore','url':base,'max_pages':1}))
    assert len(jobs)==1 and jobs[0].source_id=='123' and 'San Diego' in jobs[0].location

def test_career_page_seed_and_jsonld():
    url='https://smallbio.example/careers'
    html='''<html><body><h2>Director of Bioinformatics</h2><script type="application/ld+json">{"@type":"JobPosting","title":"Senior Microbiome Data Scientist","url":"https://smallbio.example/jobs/1","identifier":{"value":"1"},"jobLocation":{"address":{"addressLocality":"Carlsbad","addressRegion":"CA","addressCountry":"US"}},"description":"microbiome metagenomics Python"}</script></body></html>'''
    a=CareerPageAdapter(); a.session=Session({url:Resp(html)})
    jobs=list(a.fetch({'name':'Metabiomics','url':url,'default_location':'Carlsbad, CA','seed_titles':['Director of Bioinformatics']}))
    titles={j.title for j in jobs}
    assert 'Senior Microbiome Data Scientist' in titles and 'Director of Bioinformatics' in titles
