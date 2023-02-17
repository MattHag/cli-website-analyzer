from website_checker.analyze.result import Status
from website_checker.check.cookies import CheckCookies


def test_analyze_cookies(page):
    expected_cookies = [c.name for c in page.cookies]

    res = CheckCookies().check(page)

    assert "cookie" in res.title.lower()
    assert res.result["list"] == expected_cookies
    assert res.status == Status.WARNING.value


def test_analyze_no_cookies(page):
    page.cookies = []
    res = CheckCookies().check(page)

    assert "no cookies" in res.result["text"].lower()
