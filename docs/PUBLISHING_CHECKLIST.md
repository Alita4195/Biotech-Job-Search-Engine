# Maintainer publishing checklist

Before publishing this repository broadly:

- [ ] Choose the final repository name and description.
- [ ] Review `LICENSE` and change the license if desired.
- [ ] Add maintainer/contact information where you want it publicly visible.
- [ ] Confirm no resume, completed calibration workbook, generated reports, SQLite database, or credentials are present.
- [ ] Run `pytest -q`.
- [ ] Confirm `config/search_profile.yml` remains a generic starter profile.
- [ ] Create the repository and push the **contents** of this folder.
- [ ] Enable Dependabot alerts and secret scanning/push protection where available.
- [ ] Consider enabling GitHub Private Vulnerability Reporting.
- [ ] Run a manual GitHub Actions workflow using a personalized private fork before recommending scheduled use.
- [ ] Create a `v1.0.0` release after the initial public commit is validated.

Suggested repository description:

> Configurable biotech job-search engine with multi-ATS collectors, profile-driven scoring, human calibration, GitHub Actions scheduling, and email alerts.

Suggested topics:

`bioinformatics`, `biotech`, `job-search`, `computational-biology`, `genomics`, `github-actions`, `workday`, `greenhouse`, `career-tools`
