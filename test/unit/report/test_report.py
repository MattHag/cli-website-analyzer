import pytest

from website_checker.analyze.result import AnalyzerResult, PageResult
from website_checker.report.report import Report


class CheckResult(AnalyzerResult):
    def __init__(self, title="Test Result"):
        self.title = title
        self.description = "This is a test result"
        self.result = [{"name": "_ga"}, {"name": "_gid"}]


def page(title="Example", results=None):
    if results is None:
        results = []
    return PageResult(
        url="https://www.example.com",
        title=title,
        results=results,
    )


@pytest.fixture
def eval_data():
    return page(results=[CheckResult(), CheckResult()])


def test_single_page_report(eval_data):
    # TODO Use tmpdir
    report = Report()

    result = report.create(eval_data)

    assert result


def test_multi_page_report():
    # TODO Use tmpdir
    report = Report()

    result = report.create([page(title="Page 1"), page(title="Page 2")])

    assert result
