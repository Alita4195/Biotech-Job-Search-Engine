import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "send_job_email.py"
spec = importlib.util.spec_from_file_location("send_job_email", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_email_digest_orders_by_score_and_has_links():
    rows = [
        {"company":"LowerCo","title":"Scientist","location":"Remote","total":"72","band":"Review","url":"https://example.com/2"},
        {"company":"TopCo","title":"Staff Bioinformatics Scientist","location":"San Diego, CA","compensation":"$160,000–$220,000/yr","total":"94","band":"Exceptional","url":"https://example.com/1"},
    ]
    text = mod.build_plain_text(rows)
    assert text.index("TopCo") < text.index("LowerCo")
    assert "94 — TopCo" in text
    assert "https://example.com/1" in text
    assert "Compensation: $160,000–$220,000/yr" in text
    html = mod.build_html(rows)
    assert "Staff Bioinformatics Scientist" in html
    assert 'href="https://example.com/1"' in html


def test_load_matches_empty_file(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("")
    assert mod.load_matches(p) == []


def test_email_digest_groups_tiers_and_includes_match_reasons():
    rows = [
        {"company":"GoodCo","title":"Scientist","location":"Boston, MA","compensation":"Not listed","total":"75","role_fit":"22","domain_fit":"15","technical_fit":"14","operating_model_fit":"10","leadership_fit":"5","url":"https://example.com/g"},
        {"company":"TopCo","title":"Staff Bioinformatics Scientist","location":"San Diego, CA","compensation":"$160,000–$220,000/yr","total":"94","role_fit":"30","domain_fit":"25","technical_fit":"20","operating_model_fit":"14","leadership_fit":"8","url":"https://example.com/t"},
    ]
    rendered = mod.build_html(rows)
    assert "Exceptional fit" in rendered
    assert "Strong fit" in rendered
    assert "Why:" in rendered
    assert rendered.index("TopCo") < rendered.index("GoodCo")
