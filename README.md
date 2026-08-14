# Biotech Job Search Engine

A personalized job-search engine for biotech and life-science careers that searches company career pages directly, ranks openings against your background, and learns from the jobs you actually want to apply to.

Built for people working in areas such as bioinformatics, computational biology, genomics, sequencing, data science, microbiome, translational research, diagnostics, and adjacent life-science fields.

How it works:

```text
Resume
  ↓
Search Profile
  ↓
Company Career Sites
  ↓
ATS Collectors + Normalization
  ↓
Scoring Engine
  ↓
Ranked Matches + SQLite History
  ↓                  ↘
Human Calibration     Email Alerts
  ↓
Improved Profile / Scoring
```

This is **not an auto-apply bot**. It automates the repetitive parts of *finding and prioritizing* jobs so you can spend your time on the applications that are actually worth pursuing.

---

## Why I built this

This project started as a practical tool built during a real biotech job search. It was later generalized so the collection infrastructure could be shared while each user's ranking profile and calibration remained their own.

If it helps you find a role worth applying to, the project is doing what it was built to do.

I found that biotech job searching is fragmented.

A role that fits the same person might be called:

- Computational Biologist
- Bioinformatics Scientist
- Data Scientist
- Applications Scientist
- Staff Scientist
- Bioinformatics Manager
- Computational Scientist

At the same time, employers distribute openings across many applicant-tracking systems (ATS) and custom career sites.

That creates two separate problems:

1. **Discovery:** relevant roles are scattered across dozens or hundreds of company career pages.
2. **Ranking:** generic keyword alerts are poor at understanding which of those roles *you would actually apply to*.

This project addresses those problems separately.

**The collection layer is reusable. The ranking layer is personal.**

The engine collects jobs from company career infrastructure, stores job history, and normalizes results. A separate user profile determines what a good job looks like for you. After the first search, you can rate real jobs and recalibrate the scoring model against your actual decisions.

For more background, see [`docs/WHY_THIS_EXISTS.md`](docs/WHY_THIS_EXISTS.md).

---

## What it does

### Searches company career sites directly

The engine monitors a broad biotech and life-science company universe and supports multiple career-platform architectures, including:

- Workday
- Greenhouse
- Lever
- Ashby
- Oracle
- iCIMS
- SmartRecruiters
- Jobvite
- ADP
- SuccessFactors
- UltiPro
- custom career pages and embedded job boards

The goal is to reduce dependence on a single aggregator or job-board search.

### Builds a personalized ranking from your background

The scoring model can consider:

- role/function fit
- seniority
- scientific and application domains
- technical skills
- sequencing/genomics experience
- statistics and machine learning
- workflow/pipeline development
- cross-functional collaboration
- product/application development
- technical and people leadership
- geography and work arrangement
- explicit positive and negative signals

The starter repository contains a **generic profile**, not a universal definition of a good job.

### Learns from your decisions

A resume tells the engine what you have done. It does not fully tell the engine what you want to do next.

After your first search, the included calibration workbook lets you rate real jobs on:

- **Overall Interest** — 1 to 5
- **Would Apply?** — Yes / Maybe / No
- role/level fit
- scientific/domain fit
- technical fit
- leadership fit
- location/work-model fit
- compensation fit

You can also add historical jobs you already applied to as positive controls.

Scoring changes can then be **back-tested against your actual decisions** instead of tuned by intuition.

### Remembers what it has already seen

Job history is stored in SQLite. A scheduled run therefore distinguishes newly discovered openings from jobs that were already present in earlier searches.

### Runs automatically

The included GitHub Actions workflow can restore the previous job-history database, search the company universe, score and rank jobs, export reports, identify newly qualifying matches, optionally send them by email, and preserve state for the next run.

The public template is **manual-only by default**. Users enable scheduling after personalizing and validating their profile.

---

## Quick start

### Option A — use ChatGPT with your resume

1. Download this repository as a ZIP.
2. Start a new ChatGPT conversation.
3. Upload the repository ZIP and your resume.
4. Ask:

> Read `docs/CHATGPT_SETUP.md` and use my resume to personalize this job-search engine. Preserve the validated collectors unless there is evidence they are broken. Explain the search profile you create, then return a revised repository ZIP.

5. Review the proposed profile.
6. Follow [`docs/GITHUB_SETUP.md`](docs/GITHUB_SETUP.md).
7. Run a baseline search manually.
8. Calibrate the results using [`docs/CALIBRATION.md`](docs/CALIBRATION.md).

**Your resume does not need to be committed to GitHub.**

### Option B — configure the profile manually

Read [`docs/PERSONALIZE_FROM_RESUME.md`](docs/PERSONALIZE_FROM_RESUME.md) and edit:

```text
config/search_profile.yml
```

When you are satisfied with the profile, change:

```yaml
profile_status: starter_needs_resume_personalization
```

to:

```yaml
profile_status: personalized_ready
```

Then validate it:

```bash
python scripts/check_profile.py
```

---

## Local installation

Python 3.12 is recommended.

```bash
git clone https://github.com/dportik/Biotech-Job-Search-Engine.git
cd Biotech-Job-Search-Engine

python -m pip install -e '.[browser,dev]'
playwright install chromium
pytest -q
```

Validate the user profile:

```bash
python scripts/check_profile.py
```

Run a search:

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

---

## First-run workflow

1. **Personalize the search profile.** Use your resume plus your actual goals.
2. **Run a broad baseline search.** Do not over-optimize before seeing real results.
3. **Calibrate using real jobs.** Rate at least 25–30 openings; more is better.
4. **Add historical positives.** Include jobs you already applied to if you have the descriptions.
5. **Back-test scoring changes.** Look for systematic false positives and false negatives.
6. **Enable scheduling and email.** Do this only after the baseline looks useful.

Open:

```text
calibration/Job_Match_Calibration_Template.xlsx
```

for the calibration workflow.

---

## Why calibration matters

A job search is not fully specified by a resume.

Two candidates with similar histories might disagree about:

- whether Principal Scientist is appropriate
- whether people management is desirable
- whether applications/customer-facing work is attractive
- whether oncology, microbiome, diagnostics, or drug discovery is the preferred domain
- whether a hybrid Bay Area job is worth pursuing
- what compensation makes relocation worthwhile

The calibration workflow captures these preferences from **behavioral evidence**.

A historical job you actually applied to can be especially useful because it tells the model:

> *This is the kind of opportunity I actually choose to pursue.*

See [`docs/CALIBRATION.md`](docs/CALIBRATION.md).

---

## GitHub Actions

The repository includes:

```text
.github/workflows/daily-job-search.yml
```

The public template supports manual execution but does not schedule searches automatically.

After personalization and a successful baseline run, you can add:

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: '35 7 * * *'
      timezone: 'America/Los_Angeles'
```

The workflow persists `jobs.sqlite` between successful runs using GitHub Actions artifacts.

Optional email notifications can be configured with repository secrets.

Full instructions: [`docs/GITHUB_SETUP.md`](docs/GITHUB_SETUP.md).

---

## Privacy

Do not commit:

- resumes
- cover letters
- completed calibration workbooks
- email credentials
- API tokens
- SMTP passwords
- generated job history
- private application notes

The included `.gitignore` excludes common personal/generated files.

For a personal deployment, a **private GitHub repository is recommended**.

See [`docs/PRIVACY_AND_SECURITY.md`](docs/PRIVACY_AND_SECURITY.md).

---

## Collector maintenance

Career infrastructure changes.

If a company unexpectedly returns zero jobs:

1. check its public careers page;
2. determine whether it actually has openings;
3. identify its current ATS or page structure;
4. fix the narrowest affected adapter/configuration;
5. add a regression test;
6. run the full test suite.

**Do not assume that zero jobs means the company has no openings.**

See [`docs/COMPANY_COLLECTORS.md`](docs/COMPANY_COLLECTORS.md).

---

## Repository structure

```text
.github/workflows/       GitHub Actions workflows
calibration/             Blank calibration workbook
config/                  Company universe and user search profile
docs/                    Setup, architecture, calibration, troubleshooting
scripts/                 Profile validation and email notification
src/biotech_jobs/        Collectors, storage, scoring, CLI
tests/                   Collector/scoring regression tests
```

---

## Limitations

This project is a discovery and prioritization aid—not a guarantee of completeness or suitability.

Career pages can change without notice. Some postings may be missed, parsed incompletely, duplicated, or removed between runs.

A high score does **not** mean you are qualified, the employer will interview you, the posting is still open, or you should automatically apply.

Human review remains the final decision.

The project is not affiliated with or endorsed by the employers or ATS vendors referenced in the configuration.

See [`DISCLAIMER.md`](DISCLAIMER.md).

---

## Contributing

Contributions are welcome, particularly:

- broken-collector fixes
- new ATS adapters
- parser regression tests
- location/compensation extraction improvements
- scoring-framework improvements that remain user-configurable
- documentation improvements

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md).

For security concerns, see [`SECURITY.md`](SECURITY.md).
---

## License

MIT — see [`LICENSE`](LICENSE).

---

## Acknowledgment

This project started as a practical tool built during a real biotech job search. It was later generalized so the collection infrastructure could be shared while each user's ranking profile and calibration remained their own.

If it helps you find a role worth applying to, the project is doing what it was built to do.
