import csv

from biotech_jobs.engine import Engine
from biotech_jobs.models import Job
from biotech_jobs.scoring import score_job


def test_location_is_not_overwritten_by_location_fit_on_export(tmp_path):
    job = Job(
        company="Example", title="Staff Bioinformatics Scientist", location="San Diego, CA",
        url="https://example.com/job/1", source="fixture", source_id="1",
        description="bioinformatics genomics sequencing Python pipeline product development",
    )
    score = score_job(job)
    row = job.to_dict(); row.update(score.to_dict()); row.update({"alert_eligible": True, "is_new": True})
    out = tmp_path / "jobs.csv"
    Engine.export_csv([row], out, min_score=0)
    exported = next(csv.DictReader(out.open()))
    assert exported["location"] == "San Diego, CA"
    assert exported["location_fit"] == "5"