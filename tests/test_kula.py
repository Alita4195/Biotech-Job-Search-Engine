from biotech_jobs.adapters.kula import KulaAdapter, _jobposting_jsonld
from bs4 import BeautifulSoup

BOARD='''<html><body>
<a href="/10xgenomics/48910">Staff Data Scientist</a>
<a href="/10xgenomics/51443?x=1">Staff Mechanical Engineer</a>
<a href="/privacy">Privacy</a>
</body></html>'''
DETAIL='''<html><head><script type="application/ld+json">{
"@context":"https://schema.org","@type":"JobPosting","title":"Staff Data Scientist, Computational Biology",
"datePosted":"2026-08-10","employmentType":"FULL_TIME","description":"<p>Python genomics workflows</p>",
"jobLocation":{"@type":"Place","address":{"addressLocality":"Pleasanton","addressRegion":"CA","addressCountry":"US"}}
}</script></head><body><h1>fallback</h1></body></html>'''

def test_kula_link_discovery_and_jsonld():
    links=KulaAdapter._detail_links(BOARD,'https://careers.kula.ai/10xgenomics','10xgenomics')
    assert links == ['https://careers.kula.ai/10xgenomics/48910','https://careers.kula.ai/10xgenomics/51443']
    data=_jobposting_jsonld(BeautifulSoup(DETAIL,'html.parser'))
    assert data['title'].startswith('Staff Data Scientist')
