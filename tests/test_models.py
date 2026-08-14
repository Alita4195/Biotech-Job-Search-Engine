from biotech_jobs.models import Job

def test_stable_key_is_stable():
    a = Job(company="Natera", title="A", location="x", url="u", source="greenhouse", source_id="123")
    b = Job(company="Natera", title="B", location="y", url="u2", source="greenhouse", source_id="123")
    assert a.stable_key == b.stable_key
