# Privacy and security

## Keep personal data out of the repository

You do not need to commit a resume. Use the resume locally or in your chosen assistant to derive `config/search_profile.yml`, then keep the original document elsewhere.

Before publishing a fork, review the profile for identifying or sensitive information. Prefer abstract preferences and skill/domain terms over personal history.

## Never commit credentials

SMTP passwords, Google App Passwords, tokens, API keys and other credentials must not be placed in YAML, Python files, documentation examples, or committed `.env` files.

For GitHub Actions, use repository/environment secrets and grant the workflow only the permissions it needs.

## Job-search data

`output/jobs.sqlite`, `ranked_jobs.csv`, `new_matches.csv`, and completed calibration workbooks can reveal job-search activity and preferences. They are ignored by the repository configuration and should normally remain private.

## Public forks

Before making a personalized fork public:

- remove resumes and cover letters;
- remove completed calibration workbooks;
- remove generated job reports/history;
- replace personal email addresses;
- inspect git history for accidentally committed secrets;
- rotate any credential that was ever committed.

## Dependency and repository security

For public repositories, consider enabling GitHub Dependabot alerts, secret scanning/push protection, and code scanning where appropriate. Review workflow logs after configuration changes to make sure secrets are not printed.
