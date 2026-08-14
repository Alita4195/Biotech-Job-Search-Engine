from biotech_jobs.models import Job
from biotech_jobs.scoring import score_job
from biotech_jobs.store import JobStore
from biotech_jobs.engine import Engine


def test_upsert_reports_new_only_once(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite")
    job = Job(company="Example", title="Staff Bioinformatics Scientist", location="San Diego, CA",
              url="https://example/jobs/1", source="fixture", source_id="1",
              description="genomics sequencing Python pipeline computational biology")
    score = score_job(job)
    assert store.upsert(job, score, now="2026-08-11T18:00:00+00:00") is True
    assert store.upsert(job, score, now="2026-08-12T18:00:00+00:00") is False


def test_new_only_export(tmp_path):
    rows = [
        {"company":"A","title":"New","total":90,"is_new":True},
        {"company":"B","title":"Old","total":95,"is_new":False},
        {"company":"C","title":"Low","total":60,"is_new":True},
    ]
    out = tmp_path / "new.csv"
    n = Engine.export_csv(rows, out, min_score=70, new_only=True)
    assert n == 1
    text = out.read_text()
    assert "New" in text and "Old" not in text and "Low" not in text
