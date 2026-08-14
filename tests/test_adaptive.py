from biotech_jobs.adapters.adaptive import parse_rendered_jobs

HTML='''<html><head><script type="application/ld+json">{
"@context":"https://schema.org","@type":"JobPosting","title":"Senior Machine Learning Scientist",
"url":"https://www.adaptivebiotech.com/career-listings/jobs/1234",
"description":"<p>Develop machine learning methods for immune sequencing.</p>",
"identifier":{"@type":"PropertyValue","value":"1234"},
"jobLocation":{"@type":"Place","address":{"addressLocality":"Seattle","addressRegion":"WA","addressCountry":"US"}}
}</script></head><body></body></html>'''

def test_adaptive_rendered_jsonld():
    jobs=parse_rendered_jobs(HTML, {'name':'Adaptive Biotechnologies'})
    assert len(jobs)==1
    assert jobs[0].source_id=='1234'
    assert jobs[0].location=='Seattle, WA, US'
