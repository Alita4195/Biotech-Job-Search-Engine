# Contributing

Contributions are welcome, especially:

- fixes for broken company collectors;
- new ATS adapters with tests;
- parsing improvements for title, location, description or compensation;
- scoring-framework improvements that remain user-configurable;
- documentation and setup improvements.

## Development setup

```bash
python -m pip install -e '.[browser]'
playwright install chromium
pytest -q
```

## Pull requests

Please keep changes focused. For collector fixes, include evidence of the failure mode and a regression test where practical. For scoring changes, avoid embedding one person's preferences into global code when the behavior belongs in `config/search_profile.yml`.

Do not include resumes, completed calibration files, email addresses, credentials, tokens, or private job-search history in issues, fixtures, commits, or pull requests.

## Collector philosophy

Prefer structured/public ATS endpoints when available. Do not add code intended to bypass authentication, CAPTCHAs, anti-bot controls, or other access restrictions.

## Reporting bugs

For ordinary bugs, open a GitHub issue with the company, adapter, error/warning, and a sanitized log excerpt. Never paste secrets into an issue.

For security problems, follow `SECURITY.md`.
