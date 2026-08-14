# Calibration — Teach the Engine Your Preferences

Resume-based scoring gets you a useful first pass. Calibration is what makes the ranking personal.

## Step 1: Run a baseline search

Run the GitHub workflow manually after personalizing `config/search_profile.yml`. Download `ranked_jobs.csv` from the reports artifact.

## Step 2: Build the review workbook

Use `calibration/Job_Match_Calibration_Template.xlsx`.

Fastest method: upload both the workbook and `ranked_jobs.csv` to ChatGPT and say:

> Populate the Match Review sheet with every job from ranked_jobs.csv. Include company, title, engine score, URL, published salary range, and the captured job description. Preserve all dropdowns and return the populated XLSX to me.

## Step 3: Rate the jobs

For each job, start with:

- **Overall Interest:** 1–5
- **Would Apply?:** Yes / Maybe / No

Then rate the explanatory dimensions where useful. Do not feel obligated to write long notes.

Aim for at least **25–30 rated jobs**. Forty to sixty gives a better calibration set.

## Step 4: Add known positives

Add 2–5 jobs you already applied to, interviewed for, or would definitely pursue. These are extremely valuable because they represent real behavior. If a posting is no longer live, paste the archived job description into the workbook.

Mark:

- `Application Status = Applied` (if true)
- `Calibration Source = Historical`
- `Overall Interest = 5 - Definitely apply`
- `Would Apply? = Yes`

## Step 5: Ask ChatGPT to calibrate

Upload:

- completed calibration workbook
- current engine ZIP
- optionally the latest `ranked_jobs.csv`

Use this prompt:

> Analyze my calibration ratings against the current engine scores. Identify systematic false positives and false negatives by role family, seniority, scientific domain, technical fit, leadership, location/work model, and compensation. Revise config/search_profile.yml only where the data supports a change. Back-test the new profile against all rated jobs and my historical positive controls. Preserve the company collectors and SQLite compatibility. Return a new production ZIP and a CSV showing old score, new score, and my rating.

## Step 6: Do not overfit

One unusual posting should not cause a major weight change. Prefer repeated patterns. Explicit hard preferences (for example, “I will not apply to Director roles”) can justify a gate/penalty even with few examples.

## Step 7: Iterate slowly

Once the ranking looks good, run it for a few weeks. Save real apply/not-apply decisions and recalibrate after another meaningful batch rather than tweaking after every daily email.
