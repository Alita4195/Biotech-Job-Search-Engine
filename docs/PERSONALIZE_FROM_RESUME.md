# Personalize the Search Criteria from Your Resume

The reusable collector engine is already configured. Your main task is to personalize `config/search_profile.yml`.

## Recommended method: let ChatGPT translate your resume

Upload this ZIP and your resume to a new ChatGPT conversation and use the prompt in `START_HERE.md`. ChatGPT should edit only the profile/scoring layer first.

## What should come from your resume

Create a profile based on demonstrated experience and your actual target roles, not every keyword appearing once on the resume.

1. **Role families.** Put the titles you actively want in the highest `role_rules`. Put adjacent roles lower.
2. **Scientific domains.** Raise weights for areas where you have strong experience and want to continue working.
3. **Technical fit.** Include tools/methods that matter for the jobs you want; avoid rewarding generic terms that occur in every posting.
4. **Operating model.** Decide whether you value research, product development, clinical/diagnostic work, applications/customer-facing science, wet-lab collaboration, etc.
5. **Leadership.** Reward leadership only to the degree you want it in your next role.
6. **Seniority.** Use `seniority_rules` to penalize or exclude levels you would not pursue.
7. **Location.** Edit the `location` section. Disable it entirely if geography should not gate alerts.

## Regex note

The `patterns` are case-insensitive regular expressions. Simple fragments such as `bioinformatic`, `metagenom`, or `sequenc` intentionally match word variants. If you are unfamiliar with regex, ask ChatGPT to make the edits.

## First-run philosophy

The initial personalized profile should be broad enough to avoid false negatives. Calibration is where precision improves. It is better to review some imperfect matches once than to permanently hide a whole class of jobs you might want.
