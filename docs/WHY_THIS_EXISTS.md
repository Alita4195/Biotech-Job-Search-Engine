# Why this exists

Job discovery in biotech is unusually fragmented. Roles with very similar responsibilities may be called *Computational Biologist*, *Bioinformatics Scientist*, *Applications Scientist*, *Data Scientist*, *Principal Scientist*, or something else entirely. At the same time, company career pages are distributed across many ATS platforms and custom websites.

A single job-board keyword alert therefore has two distinct problems:

1. **Recall:** it may never surface a relevant opening.
2. **Ranking:** when it does surface jobs, keyword overlap is a poor proxy for whether a particular person would actually apply.

This project was created to address those problems separately.

## 1. Build a durable collection layer

The engine searches company career infrastructure directly. Instead of assuming every company uses the same API, it uses adapters for common ATS systems and targeted collectors for unusual sites.

The company universe and collectors are shared infrastructure. When a collector fails, the preferred response is to diagnose that company or ATS—not to redesign unrelated parts of the engine.

## 2. Make scoring explicitly personal

Two candidates with similar resumes can rationally rank the same job very differently because of seniority, scientific interests, management goals, location, compensation, customer-facing work, regulatory context, or preferred balance between research and product development.

For that reason, the scorer reads a user-editable `config/search_profile.yml`. The profile contains role rules, scientific-domain rules, technical evidence, operating-model signals, leadership signals, seniority adjustments, mismatch penalties, interaction bonuses, and location rules.

## 3. Calibrate against decisions, not intuition

Resume-derived scoring is only an initialization.

The more important step is to collect real human ratings from the first search results. The calibration workbook asks the user whether they would apply and why. Historical applications can be added as positive controls, including expired postings if the job description is available.

Changes to scoring should then be back-tested against those ratings. This makes it possible to identify systematic false positives and false negatives instead of endlessly adding keywords.

## 4. Preserve history

The SQLite database records previously seen jobs. This prevents every scheduled run from emailing the entire current market. The normal daily experience should be: *what new, relevant jobs appeared since the last successful run?*

## Design philosophy

- Prefer explicit, inspectable scoring over opaque ranking.
- Preserve working collectors when changing personal preferences.
- Treat zero-result collectors skeptically until the careers page is verified.
- Favor reproducible tests for parser/collector fixes.
- Keep credentials out of source control.
- Keep resumes and personal calibration data out of the public repository.
- Optimize for useful human review, not for a perfect numerical score.
