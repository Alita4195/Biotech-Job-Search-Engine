from biotech_jobs.compensation import parse_compensation, extract_greenhouse_pay_html


def test_greenhouse_pay_transparency_spans_are_extracted_before_cleanup():
    html = '''
    <div class="content-pay-transparency"><div class="pay-input">
      <div class="description">The pay range is listed and actual compensation packages vary.</div>
      <div class="title">Remote USA</div>
      <div class="pay-range"><span>$166,600</span><span class="divider">&mdash;</span><span>$202,000 USD</span></div>
    </div></div>
    '''
    raw = extract_greenhouse_pay_html(html)
    assert "$166,600" in raw and "$202,000 USD" in raw
    info = parse_compensation("", html)
    assert info.minimum == 166600
    assert info.maximum == 202000
    assert info.currency == "USD"
    assert info.period == "year"
    assert info.text == "$166,600–$202,000/yr"


def test_tempus_labeled_range_without_leading_currency_symbol():
    text = "Pay Range: 100,000 - 140,000 USD The expected salary range above is applicable if the role is performed from California."
    info = parse_compensation("", text)
    assert info.minimum == 100000
    assert info.maximum == 140000
    assert info.currency == "USD"
    assert info.period == "year"
    assert info.text == "$100,000–$140,000/yr"


def test_greenhouse_html_parser_handles_exact_natera_shape():
    html = '''<ul><li>Experience building pipelines.</li></ul>
    <div class="content-pay-transparency"><div class="pay-input">
    <div class="description">The pay range is listed and actual compensation packages are based on a wide array of factors.</div>
    <div class="title">Remote USA</div><div class="pay-range"><span>$130,900</span><span class="divider">&mdash;</span><span>$163,600 USD</span></div>
    </div></div><div class="content-conclusion"><p>OUR OPPORTUNITY</p></div>'''
    info = parse_compensation("Not listed", html)
    assert info.text == "$130,900–$163,600/yr"
