import json
from biotech_jobs.adapters.foundation import FoundationMedicineAdapter

SEARCH_HTML = '''<html><body><a href="/jobs/123/senior-scientist-computational-biology">Senior Scientist, Computational Biology</a></body></html>'''
DETAIL_HTML = '''<html><body><h1>Senior Scientist, Computational Biology</h1><script type="application/ld+json">%s</script></body></html>''' % json.dumps({
    "@type":"JobPosting","title":"Senior Scientist, Computational Biology",
    "identifier":{"value":"123"},"description":"<p>Genomics and Python pipeline development.</p>",
    "jobLocation":{"address":{"addressLocality":"Boston","addressRegion":"MA","addressCountry":"US"}}
})

class FixtureFoundation(FoundationMedicineAdapter):
    def _get_html(self, url):
        return SEARCH_HTML if "/jobs/search" in url else DETAIL_HTML


def test_foundation_adapter_parses_server_rendered_jobs():
    adapter = FixtureFoundation()
    jobs = list(adapter.fetch({"name":"Foundation Medicine","url":"https://careers.foundationmedicine.com/jobs/search","max_pages":1}))
    assert len(jobs) == 1
    assert jobs[0].source_id == "123"
    assert jobs[0].title == "Senior Scientist, Computational Biology"
    assert jobs[0].location == "Boston, MA, US"
    assert "Genomics" in jobs[0].description
