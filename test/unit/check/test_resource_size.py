import pytest

from website_checker.analyze.result import Status
from website_checker.check.resource_size import CheckResourceSize
from website_checker.crawl.resource import Resource


@pytest.mark.parametrize(
    "size_kb, expected_status",
    [
        (512, Status.OK),
        (513, Status.WARNING),
        (1024, Status.WARNING),
        (1025, Status.FAILED),
    ],
)
def test_check(size_kb, expected_status, page):
    page.elements = [Resource(url="testurl.jpg", headers={"content-length": f"{str(size_kb * 1024)}"})]

    res = CheckResourceSize().check(page)

    assert "big resources" in res.title.lower()
    assert res.status == expected_status.value
    assert "load time" in res.description
