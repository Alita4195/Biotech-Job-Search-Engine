# Architecture

The package intentionally separates two layers.

## Reusable infrastructure

- `config/companies.yml` — company universe and ATS routing
- `src/biotech_jobs/adapters/` — collectors for ATS/career systems
- `src/biotech_jobs/store.py` — SQLite history/deduplication
- `src/biotech_jobs/compensation.py` — compensation normalization
- `scripts/send_job_email.py` — email digest
- `.github/workflows/daily-job-search.yml` — scheduled execution/state persistence

These should normally remain unchanged when a new person adopts the engine.

## Personal layer

- `config/search_profile.yml` — target roles, domains, technical evidence, seniority, penalties, location rules
- `src/biotech_jobs/scoring.py` — generic profile-driven scoring interpreter
- `calibration/Job_Match_Calibration_Template.xlsx` — human feedback data

Personalization should happen here first.

## Scoring model

The default profile produces a 0–100 score from:

- Role fit: up to 30
- Scientific/domain fit: up to 25
- Technical fit: up to 20
- Operating-model fit: up to 15
- Leadership fit: up to 10

Seniority rules, mismatch penalties, and optional interaction bonuses are added afterward. The score is clamped to 0–100.

`ranked_jobs.csv` contains all current jobs at or above the configured threshold that pass the location eligibility gate. It is **not hard-coded to a fixed number of rows**.
