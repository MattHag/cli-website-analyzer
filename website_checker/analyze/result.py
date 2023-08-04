import base64
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, List

from website_checker.analyze.result_data import StatusSummary, TestDescription
from website_checker.report.report_data import ReportData


class Status(IntEnum):
    OK = 1
    WARNING = 2
    FAILED = 3

    def __str__(self):
        return self.name.lower()


@dataclass
class Result:
    title: str
    description: str
    result: dict
    status: Status


class PageEvaluation:
    """Represents the analyzer results for a single URL."""

    def __init__(self, url: str, title: str, results=None, screenshot: Any = None):
        if results is None:
            results = []
        self.url = url
        self.title = title
        self.results = results
        self.status = None  # worst status of all results
        self.tags: List[str] = []
        self.screenshot = screenshot

    def add_result(self, evaluation: Result):
        self.results.append(evaluation)
        self.results.sort(key=lambda x: x.title)

    def set_tags(self, tags: List[str]):
        """Shows tags for this page."""
        self.tags = tags

    def update_page_status(self):
        """Updates status of page to the worst status of all results."""
        self.status = sorted(self.results, key=lambda x: x.status, reverse=True)[0].status


def adapter(eval_pages: List[PageEvaluation]) -> ReportData:
    """Converts analyzer results to a format for the report."""
    if not eval_pages:
        raise ValueError("No pages to evaluate.")
    eval_pages = sort_by_url(eval_pages)
    sitemap_list = sort_by_url(eval_pages)

    for page in eval_pages:
        page.update_page_status()

    summary = create_status_summary(eval_pages)
    descriptions = collect_test_descriptions(eval_pages)
    common_tags = collect_common_tags(eval_pages)

    first_page = eval_pages[0]
    report_data = ReportData(
        url=first_page.url,
        summary=summary,
        sitemap=sitemap_list,
        pages=eval_pages,
        descriptions=descriptions,
    )
    if first_page.screenshot:
        screenshot_bytes = base64.b64encode(first_page.screenshot).decode()
        report_data.screenshot = screenshot_bytes
    if common_tags:
        report_data.tags = common_tags
    return report_data


def collect_test_descriptions(evaluated_pages: List[PageEvaluation]) -> List[TestDescription]:
    """Returns unique tests and their descriptions."""
    descriptions = {}
    for page in evaluated_pages:
        for result in page.results:
            if result.description:
                descriptions[result.title] = result.description

    res = []
    for title, description in descriptions.items():
        res.append(TestDescription(title=title, description=description))
    return sorted(res, key=lambda x: x.title)


def create_status_summary(evaluated_pages: List[PageEvaluation]) -> List[StatusSummary]:
    """Generates a summary with the worst status of each test type."""
    test_summary: dict = {}
    for page in evaluated_pages:
        for result in page.results:
            default_value = StatusSummary(title=result.title, status=result.status)
            entry = test_summary.get(result.title, default_value)
            if result.status > entry.status:
                entry.status = result.status
            test_summary[result.title] = entry
    return sorted(test_summary.values(), key=lambda x: x.title)


def collect_common_tags(evaluated_pages: List[PageEvaluation]) -> List[str]:
    """Collects all tags that are present on all pages."""
    common_tags = []
    tags = list(set([tag for page in evaluated_pages for tag in page.tags]))
    for tag in tags:
        if all([tag in page.tags for page in evaluated_pages]):
            common_tags.append(tag)
    common_tags.sort()
    return common_tags


def sort_by_url(objects: list):
    """Sorts a list of objects by their url attribute.

    Any object with a url attribute can be used.
    """
    return sorted(objects, key=lambda page: (page.url.rstrip("/"), page))
