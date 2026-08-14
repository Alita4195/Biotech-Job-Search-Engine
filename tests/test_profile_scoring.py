from biotech_jobs.models import Job
from biotech_jobs.scoring import score_job, load_profile, alert_location_eligible

def job(title, desc="", location="US Remote"):
    return Job(company="Test",title=title,location=location,url="https://example.com/job/1",source="x",source_id=title,description=desc)

def test_profile_loads():
    p=load_profile(force=True)
    assert p["role_rules"] and p["domain_rules"]

def test_core_role_beats_generic_data_science():
    core=job("Senior Bioinformatics Scientist", "NGS sequencing Python pipelines statistics")
    generic=job("Senior Data Scientist", "generic analytics dashboards Python")
    assert score_job(core).total > score_job(generic).total

def test_non_us_gate():
    assert alert_location_eligible(job("Bioinformatics Scientist", location="Paris, France")) is False
    assert alert_location_eligible(job("Bioinformatics Scientist", location="US Remote")) is True
