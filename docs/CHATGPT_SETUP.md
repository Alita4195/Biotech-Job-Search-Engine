# ChatGPT-assisted personalization

You are helping a new user personalize and deploy this biotech job-search engine. Treat this file as the handoff specification.

## First response / workflow

1. Read this repository/ZIP, especially:
   - `START_HERE.md`
   - `config/search_profile.yml`
   - `config/companies.yml`
   - `src/biotech_jobs/scoring.py`
   - `.github/workflows/daily-job-search.yml`
   - `docs/PERSONALIZE_FROM_RESUME.md`
   - `docs/CALIBRATION.md`
2. Read the user's attached resume. If no resume is attached, ask them to upload it before changing scoring.
3. Build a concise **job-fit profile** from the resume and the user's stated preferences. Ask only about genuinely unresolved high-impact constraints such as target seniority, geography/remote requirements, compensation floor, and role families to exclude.
4. Edit **`config/search_profile.yml`**, not the collectors, to represent that person. Set `profile_status: personalized_ready`.
5. Keep the company/ATS collector infrastructure intact unless the user explicitly asks to change the company universe or a collector demonstrably fails.
6. Run the repository tests after edits and return a new ZIP.
7. Explain that the first run is a baseline and the scoring is provisional until calibrated.

## Resume-to-profile translation rules

Derive evidence from the resume rather than assuming all bioinformatics jobs are equivalent. Capture:

- **Target role families:** e.g. computational biology, bioinformatics, applications bioinformatics, statistical genetics, domain-specific data science.
- **Seniority:** levels to promote, penalize, or exclude.
- **Scientific domains:** only areas supported by meaningful experience or stated interest.
- **Technical skills:** languages, statistics/ML, workflow systems, HPC/cloud, sequencing analysis, data types.
- **Operating model:** product development, research, customer applications, clinical/diagnostic development, wet-lab collaboration, publications/presentations, cross-functional work.
- **Leadership:** technical leadership, project leadership, mentoring, people management.
- **Location eligibility:** country, remote/hybrid/on-site, regions to accept/reject.
- **Explicit negatives:** job families or levels the user would not pursue even if keywords overlap.

Do not copy the original creator's personal scoring assumptions. The starter profile is only a structural example.

## Initial scoring guidance

Keep the score components at approximately:
- Role fit: 30
- Scientific/domain fit: 25
- Technical fit: 20
- Operating-model fit: 15
- Leadership fit: 10

Use seniority and mismatch rules as adjustments. Avoid overfitting during initial resume personalization. The user's human calibration later is the authority.

## Calibration workflow

After a baseline production run:

1. Have the user upload `output/ranked_jobs.csv` and `calibration/Job_Match_Calibration_Template.xlsx`.
2. Populate the workbook with company, title, engine score, URL, compensation, and job description.
3. Ask the user to rate at least 25–30 jobs, preferably 40–60.
4. Encourage 2–5 **historical positive controls**: jobs already applied to or definitely worth applying to. Add the archived job description if the posting disappeared.
5. Analyze score vs. `Overall Interest` / `Would Apply?`. Identify systematic false positives/false negatives by seniority, role family, domain, technical requirements, work model, and compensation.
6. Modify weights/gates only when supported by multiple ratings or a very strong explicit preference.
7. Back-test the revised scorer against the rated set and protect known-positive controls from regression.
8. Return a new production ZIP. Preserve SQLite compatibility and collectors.

## Safety/maintenance rules

- Do not ask the user to commit passwords/tokens.
- Do not place SMTP credentials in YAML or source code.
- Do not reset/delete `output/jobs.sqlite` unless the user explicitly wants to rebuild history.
- If a collector breaks, diagnose the affected company; do not rewrite unrelated collectors.
- Do not silently accept a zero-result company as healthy unless the careers page is verified empty.
