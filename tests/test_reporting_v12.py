import csv
from biotech_jobs.engine import Engine
from biotech_jobs.models import Job
from biotech_jobs.scoring import score_job

def test_food_biotech_scoring_version_on_export(tmp_path):
    # 模拟一个发酵食品方向的岗位
    job = Job(
        company="Valio", title="Junior Scientist - Fermentation", location="Helsinki, Finland",
        url="https://example.com/job/1", source="fixture", source_id="1",
        description="Precision fermentation, lactic acid bacteria, and bioreactor scale-up.",
    )
    score = score_job(job)
    row = job.to_dict(); row.update(score.to_dict()); row.update({"alert_eligible": True, "is_new": True})
    
    out = tmp_path / "jobs.csv"
    Engine.export_csv([row], out, min_score=0)
    exported = next(csv.DictReader(out.open()))
    
    # 验证：导出的 CSV 必须带有你的专属防伪标记，且再也没有杂七杂八的旧字段了
    assert exported["scoring_version"] == "food-biotech-v1"
    assert "location_fit" not in exported  # 确认 location_fit 已经被物理蒸发