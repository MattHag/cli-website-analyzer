from website_checker.check.h1_headings import CheckH1Headings


def test_single_h1_heading(page):
    res = CheckH1Headings().check(page)

    assert "h1 headings" in res.title.lower()
    assert res.result


def test_multiple_h1_headings(page):
    expected_result = "First H1 Heading"
    page.html = f"<h1>{expected_result}</h1><h1>Second H1 Heading</h1>"

    result = CheckH1Headings().check(page)

    assert "multiple h1" in result.result.lower()
    assert expected_result.lower() in result.result.lower()


def test_no_h1_heading(page):
    page.html = ""
    result = CheckH1Headings().check(page)

    assert "no h1" in result.result.lower()
