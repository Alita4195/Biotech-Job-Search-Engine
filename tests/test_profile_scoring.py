from biotech_jobs.models import Job
from biotech_jobs.scoring import score_job, load_profile, alert_location_eligible

def job(title, desc="", location="US Remote"):
    return Job(company="Test",title=title,location=location,url="https://example.com/job/1",source="x",source_id=title,description=desc)

def test_profile_loads():
    p=load_profile(force=True)
    assert p["role_rules"] and p["domain_rules"]

def test_core_role_beats_generic_data_science():
    # 你的核心高分岗位：微生物博后，包含益生菌、发酵和Python技能
    core = job("Microbiology Postdoc", "probiotics fermentation comparative genomics python")
    
    # 边缘/普通岗位：普通数据科学家，缺乏你核心领域的关键词
    generic = job("Data Scientist", "generic analytics dashboards Python")
    
    # 断言：核心微生物岗位的总分，必须大于普通数据科学岗位
    assert score_job(core).total > score_job(generic).total

def test_non_us_gate():
    assert alert_location_eligible(job("Bioinformatics Scientist", location="Paris, France")) is False
    assert alert_location_eligible(job("Bioinformatics Scientist", location="US Remote")) is True
