# Biotech Job Search Engine

A configurable, open-source job-discovery system for biotech, genomics, computational biology, bioinformatics, and adjacent life-science roles.

It monitors public company career pages across many applicant-tracking systems (ATS), keeps persistent job history, ranks jobs against a **user-specific search profile**, and can send email alerts for newly discovered matches.

The core idea is simple:

> **Collection should be reusable; ranking should be personal.**

A generic keyword search can find jobs that *sound* relevant while ranking the wrong seniority, scientific domain, work model, or type of role. This project separates the hard engineering problem—reliably collecting jobs from heterogeneous career sites—from the personal problem of deciding what a good job looks like for a particular candidate.

## Why this project exists

This project grew out of a practical biotech job search. Three problems kept recurring:

1. Relevant openings were scattered across dozens of company career sites and many ATS platforms.
2. Conventional keyword alerts produced both false positives and false negatives.
3. A useful ranking system had to learn from the candidate's resume **and** from real apply / don't-apply decisions.

The resulting workflow combines a broad company collector universe with a profile-driven scoring model and a human calibration loop. See [`docs/WHY_THIS_EXISTS.md`](docs/WHY_THIS_EXISTS.md).

## What it does

- Collects public job postings from a large biotech/life-sciences company universe.
- Supports Greenhouse, Workday, Lever, Ashby, Oracle, iCIMS, SmartRecruiters, Jobvite, ADP, SuccessFactors, UltiPro and several custom career-site patterns.
- Persists job history in SQLite so the same opening is not repeatedly treated as new.
- Scores jobs across role fit, scientific/domain fit, technical fit, operating-model fit, and leadership fit.
- Applies configurable seniority, mismatch, interaction, and location rules.
- Exports `ranked_jobs.csv`, `new_matches.csv`, and a run summary.
- Can run daily in GitHub Actions and email newly qualifying jobs.
- Includes a calibration workbook for improving the scoring model from human ratings.
- Can be personalized manually or with ChatGPT using a resume as the starting evidence.

## Quick start

### Option A — personalize with ChatGPT

1. Download this repository as a ZIP.
2. Start a new ChatGPT conversation and upload the ZIP **plus your resume**.
3. Ask:

   > Read `docs/CHATGPT_SETUP.md` and use my resume to personalize this job-search engine. Preserve the validated collectors unless there is evidence they are broken. Return a revised repository ZIP and explain the profile you created.

4. Review the proposed profile before using it.
5. Follow [`docs/GITHUB_SETUP.md`](docs/GITHUB_SETUP.md).
6. Run a baseline search.
7. Calibrate the results using [`docs/CALIBRATION.md`](docs/CALIBRATION.md).

Your resume does **not** need to be committed to the repository.

### Option B — configure manually

1. Clone/download the repository.
2. Read [`docs/PERSONALIZE_FROM_RESUME.md`](docs/PERSONALIZE_FROM_RESUME.md).
3. Edit `config/search_profile.yml`.
4. Change `profile_status` to `personalized_ready`.
5. Install and test:

```bash
python -m pip install -e '.[browser]'
playwright install chromium
pytest -q
python scripts/check_profile.py
```

6. Run the engine:

```bash
biotech-jobs \
  --config config/companies.yml \
  --db output/jobs.sqlite \
  --csv output/ranked_jobs.csv \
  --new-csv output/new_matches.csv \
  --min-score 65 \
  --request-timeout 12 \
  --company-timeout 75
```

## Personalization and calibration

`config/search_profile.yml` is intentionally a **starter profile**, not a universal definition of a good biotech job.

A good setup has two stages:

**Resume initialization.** Translate the candidate's actual experience and goals into target roles, domains, technical strengths, leadership signals, seniority rules, geography, and explicit negatives.

**Human calibration.** After the first broad run, rate real results. The included workbook captures overall interest, whether you would apply, and the reasons behind that decision. Historical jobs you already applied to can be added as positive controls. Then back-test scoring changes against the rated set rather than adjusting weights by intuition alone.

See [`docs/CALIBRATION.md`](docs/CALIBRATION.md).

## Repository layout

```text
.github/workflows/       Scheduled GitHub Actions workflow
calibration/             Blank calibration workbook
config/                  Company universe and personal search profile
docs/                    Setup, architecture, calibration and troubleshooting
scripts/                 Profile validation and email notification
src/biotech_jobs/        Collector, storage, scoring and CLI code
tests/                   Collector/scoring regression tests
```

## GitHub Actions and email

The included workflow can run on a daily schedule or manually. It restores the previous SQLite history from the prior successful run, executes the search, emails only new qualifying matches when SMTP is configured, and uploads state/reports as workflow artifacts.

Sensitive values belong in **GitHub Actions repository secrets**, never in source files. See [`docs/GITHUB_SETUP.md`](docs/GITHUB_SETUP.md).

## Important limitations

Career sites change. A collector that works today may break later, and a zero-result response is not automatically proof that a company has no openings. The engine includes diagnostics and tests, but it cannot guarantee completeness.

Scores are recommendations, not objective measures of job suitability. The starter profile must be personalized, and users should review postings themselves before applying.

This project is not affiliated with, endorsed by, or sponsored by any company or ATS represented in the configuration. It only attempts to read publicly available job-posting information. Users are responsible for complying with applicable website terms, policies, laws, and reasonable request rates.

See [`DISCLAIMER.md`](DISCLAIMER.md) and [`docs/PRIVACY_AND_SECURITY.md`](docs/PRIVACY_AND_SECURITY.md).

## Contributing

Collector fixes, new ATS adapters, parser regression tests, documentation improvements, and scoring-framework improvements are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT. See [`LICENSE`](LICENSE).
