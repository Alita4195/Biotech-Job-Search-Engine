from __future__ import annotations
import sqlite3, json
from datetime import datetime, timezone
from biotech_jobs.models import Job

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
 stable_key TEXT PRIMARY KEY, company TEXT, title TEXT, location TEXT, url TEXT,
 source TEXT, source_id TEXT, description TEXT, department TEXT, team TEXT,
 workplace_type TEXT, employment_type TEXT, published_at TEXT, updated_at TEXT,
 compensation TEXT, compensation_min REAL, compensation_max REAL, compensation_currency TEXT, compensation_period TEXT, first_seen TEXT, last_seen TEXT, active INTEGER DEFAULT 1,
 score INTEGER, band TEXT, score_json TEXT
);
CREATE TABLE IF NOT EXISTS runs (
 run_id TEXT PRIMARY KEY, started_at TEXT, completed_at TEXT, companies_attempted INTEGER,
 jobs_retrieved INTEGER, new_jobs INTEGER, errors_json TEXT
);
"""

class JobStore:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        # Forward-compatible migration for databases created before v1.2.
        existing = {row[1] for row in self.conn.execute("PRAGMA table_info(jobs)")}
        for name, sql_type in (("compensation_min", "REAL"), ("compensation_max", "REAL"),
                               ("compensation_currency", "TEXT"), ("compensation_period", "TEXT")):
            if name not in existing:
                self.conn.execute(f"ALTER TABLE jobs ADD COLUMN {name} {sql_type}")
        self.conn.commit()

    def upsert(self, job: Job, score, now: str | None = None) -> bool:
        now = now or datetime.now(timezone.utc).isoformat()
        existing = self.conn.execute("SELECT first_seen FROM jobs WHERE stable_key=?", (job.stable_key,)).fetchone()
        is_new = existing is None
        first_seen = existing[0] if existing else now
        self.conn.execute("""
        INSERT INTO jobs(stable_key,company,title,location,url,source,source_id,description,department,team,
          workplace_type,employment_type,published_at,updated_at,compensation,compensation_min,compensation_max,compensation_currency,compensation_period,first_seen,last_seen,active,score,band,score_json)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(stable_key) DO UPDATE SET title=excluded.title,location=excluded.location,url=excluded.url,
          description=excluded.description,department=excluded.department,team=excluded.team,workplace_type=excluded.workplace_type,
          employment_type=excluded.employment_type,published_at=excluded.published_at,updated_at=excluded.updated_at,
          compensation=excluded.compensation,compensation_min=excluded.compensation_min,compensation_max=excluded.compensation_max,compensation_currency=excluded.compensation_currency,compensation_period=excluded.compensation_period,last_seen=excluded.last_seen,active=1,score=excluded.score,band=excluded.band,score_json=excluded.score_json
        """, (job.stable_key, job.company, job.title, job.location, job.url, job.source, job.source_id,
               job.description, job.department, job.team, job.workplace_type, job.employment_type, job.published_at,
               job.updated_at, job.compensation, job.compensation_min, job.compensation_max, job.compensation_currency, job.compensation_period, first_seen, now, 1, score.total, score.band, json.dumps(score.to_dict())))
        self.conn.commit()
        return is_new

    def mark_missing_inactive(self, company, seen_keys):
        placeholders = ",".join("?" for _ in seen_keys)
        if seen_keys:
            self.conn.execute(f"UPDATE jobs SET active=0 WHERE company=? AND stable_key NOT IN ({placeholders})", [company, *seen_keys])
        else:
            self.conn.execute("UPDATE jobs SET active=0 WHERE company=?", (company,))
        self.conn.commit()

    def record_run(self, run_id: str, started_at: str, completed_at: str, companies_attempted: int,
                   jobs_retrieved: int, new_jobs: int, errors: list[dict]):
        self.conn.execute("""
        INSERT OR REPLACE INTO runs(run_id,started_at,completed_at,companies_attempted,jobs_retrieved,new_jobs,errors_json)
        VALUES(?,?,?,?,?,?,?)
        """, (run_id, started_at, completed_at, companies_attempted, jobs_retrieved, new_jobs, json.dumps(errors)))
        self.conn.commit()
