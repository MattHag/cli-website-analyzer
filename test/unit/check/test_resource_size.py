import pytest

from website_checker.analyze.result import Status
from website_checker.check.resource_size import (
    CONTENT_TYPES_CATEGORIZED,
    CheckResourceSize,
    resource_size_per_category,
)
from website_checker.crawl.resource import ResourceRequest


@pytest.mark.parametrize(
    "page_size_kb, expected_status",
    [
        (0, Status.OK),
        (512, Status.OK),
        (513, Status.WARNING),
        (1024, Status.WARNING),
        (1025, Status.FAILED),
        (2412, Status.FAILED),
    ],
)
def test_check_resource_sizes(page_size_kb, expected_status, page):
    request_size = page_size_kb * 1024
    page.requests = [ResourceRequest(url="test.html", sizes={"test_entry": request_size})]

    res = CheckResourceSize().check(page)

    assert res.status == expected_status
    assert "total page size" in res.title.lower()
    assert "big resources" in res.title.lower()
    assert "load time" in res.description

    if expected_status == Status.OK:
        assert "no big resources" in res.result["text"].lower()
        assert "good" in res.result["text"].lower()


@pytest.mark.parametrize(
    "nr_requests, expected_status",
    [
        (0, Status.OK),
        (1, Status.OK),
        (4, Status.OK),
        (5, Status.WARNING),
        (9, Status.WARNING),
        (10, Status.FAILED),
        (15, Status.FAILED),
    ],
)
def test_check_total_page_size(nr_requests, expected_status, page):
    element_size = 420 * 1024
    page.requests = [ResourceRequest(url="testurl.jpg", sizes={"test_entry": element_size})] * nr_requests

    res = CheckResourceSize().check(page)

    assert "big resources" in res.title.lower()
    assert res.status == expected_status
    assert "load time" in res.description

    if expected_status == Status.OK:
        assert "good" in res.result["text"].lower()


def test_resource_size_per_category(page):
    res = resource_size_per_category(page)
    total_size = sum([size for size, _ in res.values()])

    assert total_size > 0
    assert len(res) == len(CONTENT_TYPES_CATEGORIZED)
