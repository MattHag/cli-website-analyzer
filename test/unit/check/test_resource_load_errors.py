import pytest

from website_checker.analyze.result import Status
from website_checker.check.resource_load_errors import CheckResourceLoadErrors
from website_checker.crawl.resource import Resource


@pytest.mark.parametrize(
    "status_code, expected_status",
    [
        (404, Status.WARNING),
        (200, Status.OK),
    ],
)
def test_check_400_status_errors(status_code, expected_status, page):
    page.elements = [Resource(url="unknown_resource.jpg", status_code=status_code)]

    res = CheckResourceLoadErrors().check(page)

    assert res.status == expected_status.value
    assert "resource load errors" in res.title.lower()
    assert "do not load" in res.description

    if res.status == Status.OK.value:
        assert "nice" in res.result["text"].lower()
    else:
        assert len(res.result["list"]["entries"]) == 1
