import pytest

from website_checker.analyze.result import Status
from website_checker.check.accessibility_axe import CheckAccessibility, Impact
from website_checker.crawl.axe.axe_runner import AxeIssue

SEVERE_ISSUE = AxeIssue(
    "test-severe-issues",
    impact=Impact.SERIOUS.value,
    target="test-target",
    help="test-help",
    help_url="test-help-url",
    screenshot="",
)

MINOR_ISSUE = AxeIssue(
    "test-severe-issues",
    impact=Impact.MINOR.value,
    target="test-target",
    help="test-help",
    help_url="test-help-url",
    screenshot=b"",
)


@pytest.mark.parametrize(
    ["issues", "expected_status"],
    [
        ([], Status.OK),
        ([MINOR_ISSUE], Status.WARNING),
        ([SEVERE_ISSUE], Status.FAILED),
        ([SEVERE_ISSUE, MINOR_ISSUE], Status.FAILED),
    ],
)
def test_check_accessibility(issues, expected_status, page):
    page.accessibility = issues

    res = CheckAccessibility().check(page)

    assert res.title == "Automated accessibility checks"
    assert res.status == expected_status
