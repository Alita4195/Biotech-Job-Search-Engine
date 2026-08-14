# Troubleshooting

## Workflow is not visible in GitHub Actions
Confirm `.github/workflows/daily-job-search.yml` was uploaded. Hidden folders are commonly omitted by drag/drop workflows.

## Workflow appears stuck on the search step
Open the running step. The engine logs one company at a time. Large Workday boards can take tens of seconds. The workflow has a global timeout and each company has a hard timeout so one site should not block forever.

## `ZERO_RESULT_UNVERIFIED`
This means the collector returned zero jobs but the configuration does not know that the board is genuinely empty. It is a health warning, not proof that there are no jobs. Have ChatGPT inspect only that company's current careers infrastructure.

## One company errors
A single company error does not stop the full run. Repeated errors for the same company usually mean the ATS URL/tenant changed or the site is temporarily slow.

## Email step is skipped
If there are no new qualifying matches, skipping is expected. If new matches exist, confirm all required SMTP secrets are configured.

## Gmail authentication fails
Use a Google App Password rather than your normal account password. App Passwords require 2-Step Verification and may be unavailable on some managed/Advanced Protection accounts.

## Every job is “new” again
The SQLite history was not restored. Check that a prior successful workflow run has a `job-search-state` artifact. Do not delete the state unless intentionally rebuilding the baseline.

## Rankings are bad but collectors work
Do not debug ATS code. Revisit `config/search_profile.yml` and perform calibration.

## Job count suddenly collapses at one company
Compare with the company's public careers page. A collector can return nonzero but incomplete results after a careers-site redesign. Treat suspiciously low counts as a collector-quality issue.
