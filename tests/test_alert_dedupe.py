from biotech_jobs.engine import Engine

def test_alert_dedupe_keeps_highest_score_for_same_company_title():
    rows = [
        {"company":"Natera","title":"Bioinformatics Manager","total":82,"location":"A"},
        {"company":"Natera","title":"Bioinformatics Manager","total":87,"location":"Remote"},
        {"company":"Natera","title":"Lead Bioinformatician","total":83,"location":"Remote"},
    ]
    out = Engine._dedupe_alert_rows(rows)
    assert len(out) == 2
    mgr = [r for r in out if r['title']=='Bioinformatics Manager'][0]
    assert mgr['total'] == 87
