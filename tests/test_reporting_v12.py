import csv

from biotech_jobs.compensation import parse_compensation
from biotech_jobs.engine import Engine
from biotech_jobs.models import Job
from biotech_jobs.scoring import score_job
from biotech_jobs.store import JobStore


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


def test_compensation_parser_annual_range_from_description():
    info = parse_compensation("", "Actual compensation depends on experience. The anticipated wage for this position is $166,500 - $266,200 Full-time employees are also eligible for a bonus.")
    assert info.minimum == 166500
    assert info.maximum == 266200
    assert info.currency == "USD"
    assert info.period == "year"
    assert info.text == "$166,500–$266,200/yr"


def test_compensation_parser_hourly_range():
    info = parse_compensation("", "The pay range is $36.13 - $58.11/hr depending on experience.")
    assert info.minimum == 36.13
    assert info.maximum == 58.11
    assert info.period == "hour"
    assert info.text == "$36.13–$58.11/hr"


def test_compensation_not_listed_is_explicit():
    info = parse_compensation("", "No salary information is included in this posting.")
    assert info.text == "Not listed"
    assert info.minimum is None
    assert info.maximum is None


def test_store_migrates_existing_database_and_persists_compensation(tmp_path):
    import sqlite3
    db = tmp_path / "old.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE jobs (stable_key TEXT PRIMARY KEY, company TEXT, title TEXT, location TEXT, url TEXT, source TEXT, source_id TEXT, description TEXT, department TEXT, team TEXT, workplace_type TEXT, employment_type TEXT, published_at TEXT, updated_at TEXT, compensation TEXT, first_seen TEXT, last_seen TEXT, active INTEGER DEFAULT 1, score INTEGER, band TEXT, score_json TEXT)")
    conn.execute("CREATE TABLE runs (run_id TEXT PRIMARY KEY, started_at TEXT, completed_at TEXT, companies_attempted INTEGER, jobs_retrieved INTEGER, new_jobs INTEGER, errors_json TEXT)")
    conn.commit(); conn.close()
    store = JobStore(db)
    cols = {r[1] for r in store.conn.execute("PRAGMA table_info(jobs)")}
    assert {"compensation_min", "compensation_max", "compensation_currency", "compensation_period"} <= cols


def test_compensation_parser_greenhouse_trailing_usd():
    info = parse_compensation("$166,600 — $202,000 USD", "")
    assert info.minimum == 166600
    assert info.maximum == 202000
    assert info.currency == "USD"
    assert info.period == "year"
    assert info.text == "$166,600–$202,000/yr"
