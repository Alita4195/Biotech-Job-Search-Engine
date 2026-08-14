from biotech_jobs.adapters.workday import WorkdayAdapter


class FakeResponse:
    def __init__(self, data): self._data = data
    def raise_for_status(self): return None
    def json(self): return self._data


class FakeSession:
    def __init__(self):
        self.headers = {}
        self.posts = []
    def post(self, url, json, timeout, headers):
        self.posts.append((url, json))
        if json["offset"] == 0:
            return FakeResponse({
                "total": 2,
                "jobPostings": [
                    {"title": "Staff Bioinformatics Scientist", "externalPath": "/job/Staff-Bioinformatics-Scientist_43098-JOB-1", "locationsText": "San Diego, CA", "postedOn": "Posted 2 Days Ago", "bulletFields": ["43098-JOB-1"]},
                    {"title": "Scientist II", "externalPath": "/job/Scientist-II_12345-JOB", "locationsText": "Foster City, CA", "postedOn": "Posted 5 Days Ago", "bulletFields": ["12345-JOB"]},
                ]
            })
        return FakeResponse({"total": 2, "jobPostings": []})
    def get(self, url, timeout, **kwargs):
        if "43098" in url:
            return FakeResponse({"jobPostingInfo": {
                "title": "Staff Bioinformatics Scientist",
                "jobReqId": "43098-JOB-1",
                "location": "San Diego, CA",
                "jobDescription": "<p>Develop genomics pipelines using Python and NGS data.</p>",
                "timeType": "Full time"
            }})
        return FakeResponse({"jobPostingInfo": {
            "title": "Scientist II",
            "jobReqId": "12345-JOB",
            "location": "Foster City, CA",
            "jobDescription": "<p>Wet lab assay development.</p>"
        }})


def test_workday_fetch_normalizes_and_paginates():
    adapter = WorkdayAdapter()
    adapter.session = FakeSession()
    company = {"name":"Illumina","host":"illumina.wd1.myworkdayjobs.com","tenant":"illumina","board":"illumina-careers","page_size":20}
    jobs = list(adapter.fetch(company))
    assert len(jobs) == 2
    assert jobs[0].source == "workday"
    assert jobs[0].source_id == "43098-JOB-1"
    assert jobs[0].title == "Staff Bioinformatics Scientist"
    assert jobs[0].description == "Develop genomics pipelines using Python and NGS data."
    assert jobs[0].url.endswith("/en-US/illumina-careers/job/Staff-Bioinformatics-Scientist_43098-JOB-1")
    assert len(adapter.session.posts) == 1

class DetailFailureSession(FakeSession):
    def get(self, url, timeout, **kwargs):
        raise RuntimeError("transient detail failure")


def test_workday_keeps_listings_when_detail_enrichment_fails():
    adapter = WorkdayAdapter()
    adapter.session = DetailFailureSession()
    company = {"name":"Illumina","host":"illumina.wd1.myworkdayjobs.com","tenant":"illumina","board":"illumina-careers"}
    jobs = list(adapter.fetch(company))
    assert len(jobs) == 2
    assert jobs[0].title == "Staff Bioinformatics Scientist"
    assert jobs[0].source_id == "43098-JOB-1"
    assert jobs[0].location == "San Diego, CA"

class CountingSession(FakeSession):
    def __init__(self):
        super().__init__()
        self.gets = []
    def get(self, url, timeout, **kwargs):
        self.gets.append(url)
        return super().get(url, timeout, **kwargs)


def test_workday_only_enriches_candidate_titles():
    adapter = WorkdayAdapter()
    adapter.session = CountingSession()
    company = {"name":"Illumina","host":"illumina.wd1.myworkdayjobs.com","tenant":"illumina","board":"illumina-careers"}
    jobs = list(adapter.fetch(company))
    assert len(jobs) == 2
    assert len(adapter.session.gets) == 1
    assert "43098" in adapter.session.gets[0]
    assert jobs[1].description == ""

class MisleadingTotalSession(FakeSession):
    def post(self, url, json, timeout, headers):
        self.posts.append((url, json))
        offset = json["offset"]
        if offset in (0, 20, 40):
            postings = []
            for i in range(offset, offset + (20 if offset < 40 else 5)):
                postings.append({"title": f"Role {i}", "externalPath": f"/job/Role-{i}_R{i}", "bulletFields": [f"R{i}"]})
            return FakeResponse({"total": 40, "jobPostings": postings})
        return FakeResponse({"total": 40, "jobPostings": []})


def test_workday_does_not_trust_misleading_total_for_pagination():
    adapter = WorkdayAdapter()
    adapter.session = MisleadingTotalSession()
    company = {"name":"X","host":"x.myworkdayjobs.com","tenant":"x","board":"Careers","max_detail_requests":0}
    jobs = list(adapter.fetch(company))
    assert len(jobs) == 45
    assert len(adapter.session.posts) == 3
    assert adapter.last_stats["board_jobs"] == 45


class VariantSession(FakeSession):
    def post(self, url, json, timeout, headers):
        self.posts.append((url, json))
        if "/bad/" in url:
            return FakeResponse({"total": 0, "jobPostings": []})
        return FakeResponse({"total": 1, "jobPostings": [{"title":"Bioinformatics Scientist","externalPath":"/job/Bioinformatics_R1","bulletFields":["R1"]}]})


def test_workday_tries_configured_fallback_on_zero_jobs():
    adapter = WorkdayAdapter()
    adapter.session = VariantSession()
    company = {"name":"X","host":"x.myworkdayjobs.com","tenant":"bad","board":"Careers",
               "workday_fallbacks":[{"tenant":"good"}], "max_detail_requests":0}
    jobs = list(adapter.fetch(company))
    assert len(jobs) == 1
    assert any('/good/' in u for u,_ in adapter.session.posts)


class HtmlResponse:
    def __init__(self, text): self.text = text
    def raise_for_status(self): return None

class DiscoverySession:
    def __init__(self): self.headers = {}; self.posts=[]; self.gets=[]
    def post(self, url, json, timeout, headers):
        self.posts.append(url)
        if "/obvious/" in url:
            return FakeResponse({"jobPostings": []})
        return FakeResponse({"jobPostings": [{"title":"Bioinformatics Scientist","externalPath":"/job/Bioinfo_R1","bulletFields":["R1"]}]})
    def get(self, url, timeout, **kwargs):
        self.gets.append(url)
        if "/wday/cxs/hidden/RealBoard" in url:
            return FakeResponse({"jobPostingInfo":{"title":"Bioinformatics Scientist","jobReqId":"R1","jobDescription":"genomics python"}})
        return HtmlResponse('<script>window.x="/wday/cxs/hidden/RealBoard/jobs"</script>')

def test_workday_discovers_cxs_identity_from_public_html():
    adapter = WorkdayAdapter()
    adapter.session = DiscoverySession()
    company = {"name":"X","host":"x.myworkdayjobs.com","tenant":"obvious","board":"Careers","max_detail_requests":1}
    jobs = list(adapter.fetch(company))
    assert len(jobs) == 1
    assert jobs[0].source_id == "R1"
    assert any('/hidden/RealBoard/jobs' in u for u in adapter.session.posts)

class SeedFallbackSession:
    def __init__(self): self.headers = {}; self.posts=[]; self.gets=[]
    def post(self, url, json, timeout, headers):
        self.posts.append(url)
        return FakeResponse({"jobPostings": []})
    def get(self, url, timeout, **kwargs):
        self.gets.append(url)
        html = '''<html><head><script type="application/ld+json">{
          "@context":"https://schema.org", "@type":"JobPosting",
          "title":"Senior Bioinformatics Scientist",
          "description":"Develop NGS genomics pipelines in Python for diagnostic products.",
          "identifier":{"value":"R26-13229"},
          "datePosted":"2026-08-01",
          "employmentType":"FULL_TIME",
          "jobLocation":{"address":{"addressLocality":"San Diego","addressRegion":"CA","addressCountry":"US"}}
        }</script></head><body><h1>Senior Bioinformatics Scientist</h1></body></html>'''
        return HtmlResponse(html)


def test_workday_seeded_public_fallback_recovers_job_when_cxs_is_empty():
    adapter = WorkdayAdapter()
    adapter.session = SeedFallbackSession()
    seed = "https://x.myworkdayjobs.com/en-US/Careers/job/Senior-Bioinformatics-Scientist_R26-13229"
    company = {"name":"Exact Sciences","host":"x.myworkdayjobs.com","tenant":"bad","board":"Careers",
               "workday_seed_urls":[seed], "public_seed_fallback":True, "public_seed_max_pages":5,
               "max_detail_requests":0}
    jobs = list(adapter.fetch(company))
    assert len(jobs) == 1
    assert jobs[0].title == "Senior Bioinformatics Scientist"
    assert "San Diego" in jobs[0].location
    assert jobs[0].source_id == "R26-13229"
    assert jobs[0].source == "workday-public"

class MalformedLocationSession(FakeSession):
    def get(self, url, timeout, **kwargs):
        if "43098" in url:
            return FakeResponse({"jobPostingInfo": {
                "title": "Senior Staff Bioinformatics Scientist",
                "jobReqId": "43098-JOB-1",
                "location": "5",
                "jobDescription": "Develop DRAGEN NGS genomics algorithms and validation workflows.",
            }})
        return super().get(url, timeout, **kwargs)


def test_workday_repairs_numeric_location_from_external_path():
    adapter = WorkdayAdapter()
    adapter.session = MalformedLocationSession()
    company = {"name":"Illumina","host":"illumina.wd1.myworkdayjobs.com","tenant":"illumina","board":"illumina-careers"}
    # Replace the first posting's path with a location-bearing Workday path.
    original_post = adapter.session.post
    def post(url, json, timeout, headers):
        resp = original_post(url, json, timeout, headers)
        data = resp.json()
        if data.get("jobPostings"):
            data["jobPostings"][0]["externalPath"] = "/job/US---CA---San-Diego/Senior-Staff-Bioinformatics-Scientist_43098-JOB-1"
        return FakeResponse(data)
    adapter.session.post = post
    jobs = list(adapter.fetch(company))
    assert jobs[0].location == "US - CA - San Diego"


class JsShellSeedFallbackSession:
    def __init__(self): self.headers = {}; self.posts=[]; self.gets=[]
    def post(self, url, json, timeout, headers):
        self.posts.append(url)
        return FakeResponse({"jobPostings": []})
    def get(self, url, timeout, **kwargs):
        self.gets.append(url)
        return HtmlResponse('<html><head><title>Workday</title></head><body><div id="app"></div></body></html>')


def test_workday_seed_metadata_recovers_job_from_js_shell():
    adapter = WorkdayAdapter()
    adapter.session = JsShellSeedFallbackSession()
    seed = {
        "url":"https://x.myworkdayjobs.com/en-US/Careers/job/US---CA---San-Diego/Bioinformatics-Scientist_R26-13249",
        "title":"Bioinformatics Scientist",
        "location":"US - CA - San Diego",
        "description":"NGS genomics bioinformatics pipeline development in Python for diagnostic products.",
    }
    company = {"name":"Exact Sciences","host":"x.myworkdayjobs.com","tenant":"bad","board":"Careers",
               "workday_seed_urls":[seed], "public_seed_fallback":True, "public_seed_max_pages":5,
               "max_detail_requests":0}
    jobs = list(adapter.fetch(company))
    assert len(jobs) == 1
    assert jobs[0].title == "Bioinformatics Scientist"
    assert jobs[0].location == "US - CA - San Diego"
    assert jobs[0].source_id == "R26-13249"
    assert "NGS genomics" in jobs[0].description
