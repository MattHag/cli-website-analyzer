import pytest

from website_checker.analyze.result import Status
from website_checker.check.resource_load_errors import CheckResourceLoadErrors
from website_checker.crawl.resource import Resource, ResourceRequest


@pytest.mark.parametrize(
    "status_code, expected_status",
    [
        (404, Status.WARNING),
        (403, Status.WARNING),
        (200, Status.OK),
    ],
)
def test_check_status_400_errors(status_code, expected_status, page):
    page.elements = [Resource(url="unknown_resource.jpg", status_code=status_code)]

    res = CheckResourceLoadErrors().check(page)

    assert res.status == expected_status
    assert "resource load errors" in res.title.lower()
    assert "do not load" in res.description

    if res.status != Status.OK:
        assert len(res.result["list"]["entries"]) == 1


def test_check_aborted_requests(page):
    page.failed_requests = [ResourceRequest(url="unknown_resource.jpg", failure="DNS lookup failed")]

    res = CheckResourceLoadErrors().check(page)

    assert res.status == Status.WARNING
    assert "unknown_resource.jpg, DNS lookup failed" == res.result["list"]["entries"][0]
