# GitHub setup — your personal scheduled search

## 1. Create your own repository

For a personal search, create a new repository (for example `my-biotech-job-search`). **Private is recommended** because your personalized profile and workflow artifacts may reveal career preferences. If you are publishing/contributing to the generic engine itself, use a separate public repository that contains no personal outputs or calibration data.

GitHub documentation: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository

## 2. Upload the package contents

Unzip the personalized package on your computer. Upload the **contents of the folder**, not the outer ZIP itself. The repository root should contain files/folders such as:

- `.github/`
- `config/`
- `src/`
- `scripts/`
- `tests/`
- `pyproject.toml`
- `START_HERE.md`

GitHub's web UI supports **Add file → Upload files** and drag/drop. Hidden folders such as `.github` can be easy to miss on some systems, so confirm `.github/workflows/daily-job-search.yml` exists in the repository after upload.

GitHub documentation: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

## 3. Enable/run GitHub Actions

Open the repository's **Actions** tab. The workflow is named **Daily biotech job search**. Use **Run workflow** for the first manual run.

The package uses a scheduled GitHub Actions workflow plus `workflow_dispatch` for manual runs. The schedule is in `.github/workflows/daily-job-search.yml` and supports an IANA timezone string. Edit the cron/timezone if you want a different delivery time.

GitHub workflow schedule reference: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule

## 4. First baseline run

For the first run, you may want to leave email secrets unconfigured. The engine has no previous SQLite history, so currently open jobs may all be considered first-seen. After the successful run, GitHub saves `output/jobs.sqlite` as the `job-search-state` artifact. Future runs restore that history.

Download the reports artifact and inspect:

- `ranked_jobs.csv` — current qualifying matches
- `new_matches.csv` — qualifying jobs first seen on this run
- `run_summary.json` — counts/errors/warnings

Do **not** routinely delete the state artifact or SQLite history; doing so makes existing jobs look new again.

## 5. Configure email alerts

Repository → **Settings → Secrets and variables → Actions → New repository secret**.

Add:

- `SMTP_HOST` — for Gmail use `smtp.gmail.com`
- `SMTP_PORT` — Gmail STARTTLS: `587`
- `SMTP_USERNAME` — your sending Gmail address
- `SMTP_PASSWORD` — Google App Password, not your normal Google password
- `SMTP_USE_SSL` — `false` for port 587
- `EMAIL_TO` — destination email address
- `EMAIL_FROM` — optional; usually same as `SMTP_USERNAME`

GitHub secrets documentation: https://docs.github.com/en/actions/concepts/security/secrets

For Gmail, Google App Passwords require 2-Step Verification. Google describes an App Password as a 16-digit passcode for apps that cannot use Sign in with Google. Some managed/Advanced Protection accounts may not offer App Passwords.

Google documentation: https://support.google.com/mail/answer/185833

Never commit these values into the repository.

## 6. Scheduled workflow

The public repository ships **manual-only** so an unpersonalized fork does not immediately start scheduled searches. After `config/search_profile.yml` is personalized and a manual run succeeds, edit `.github/workflows/daily-job-search.yml` so its `on:` block contains:

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: '35 7 * * *'
      timezone: 'America/Los_Angeles'
```

Change the timezone and time to your preference. GitHub's scheduler may start a scheduled workflow slightly later than the exact minute during periods of high load, so treat it as a daily delivery time rather than a real-time system.

## 7. Updating the engine later

When ChatGPT returns a calibrated or repaired ZIP:

- Replace the code/config files in GitHub.
- Preserve the prior successful `job-search-state` artifact / SQLite history.
- Run the workflow manually once.
- Review `run_summary.json` before relying on the scheduled run.

## Profile personalization guard

The workflow runs `python scripts/check_profile.py` before searching. It will intentionally fail while `profile_status` is still `starter_needs_resume_personalization`. After ChatGPT/personal setup is complete, set:

```yaml
profile_status: personalized_ready
```

This prevents the starter example from silently becoming your production ranking model.
