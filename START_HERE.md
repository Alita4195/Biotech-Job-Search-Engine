# Start here

This repository is designed to be usable by someone who did not participate in its development.

## If you just want your own job search

1. Personalize `config/search_profile.yml` from your resume and career preferences.
2. Run `python scripts/check_profile.py`.
3. Run the tests.
4. Create a GitHub repository and follow `docs/GITHUB_SETUP.md`.
5. Run the workflow manually once to establish job history.
6. Rate the initial results using `calibration/Job_Match_Calibration_Template.xlsx`.
7. Use `docs/CALIBRATION.md` to improve the ranking from your actual decisions.
8. Turn on email notifications and the daily schedule once you are satisfied with the results.

## If you are evaluating or contributing to the project

Read, in order:

- `docs/WHY_THIS_EXISTS.md`
- `docs/ARCHITECTURE.md`
- `docs/COMPANY_COLLECTORS.md`
- `CONTRIBUTING.md`
- `SECURITY.md`

## If you are using ChatGPT

Upload the repository ZIP and your resume, then tell ChatGPT to read `docs/CHATGPT_SETUP.md`. The instructions deliberately tell it to personalize the scoring profile without casually rewriting working collectors.

## One principle to remember

**Do not treat the starter score as personalized.** The company-collection layer is reusable; the ranking layer is supposed to be adapted to the individual.
