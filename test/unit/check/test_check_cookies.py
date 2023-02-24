import pytest

from website_checker.analyze.result import Status
from website_checker.check.cookies import CheckCookies
from website_checker.crawl.cookie import Cookie


@pytest.mark.parametrize(
    "cookie_names, expected_status",
    [
        (["CookieConsentBulkTicket"], Status.WARNING),
        ([], Status.OK),
    ],
)
def test_check_cookies(cookie_names, expected_status, page):
    page.cookies = [Cookie(name) for name in cookie_names]

    res = CheckCookies().check(page)

    assert res.status == expected_status
    assert res.title == "Cookies without consent"
    assert res.description

    if expected_status == Status.OK:
        assert res.result["text"]
    else:
        assert len(res.result["table"]["entries"]) == len(cookie_names)


def test_check_unknown_cookie(page):
    page.cookies = [Cookie("unknown")]

    res = CheckCookies().check(page)

    assert res.status == Status.WARNING
