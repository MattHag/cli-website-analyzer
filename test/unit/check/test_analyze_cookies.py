from website_checker.check.cookies import CheckCookies


def test_analyze_cookies(page):
    res = CheckCookies().check(page)

    assert "cookie" in res.title.lower()
    assert res.result
    for cookie in page.cookies:
        assert cookie.name in res.result


def test_analyze_no_cookies(page):
    page.cookies = []
    res = CheckCookies().check(page)

    assert "no cookies" in res.result.lower()
