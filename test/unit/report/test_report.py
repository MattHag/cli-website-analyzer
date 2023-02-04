from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from website_checker.analyze.result import AnalyzerResult, PageResult
from website_checker.report import report


@pytest.fixture
def tmp_file(tmp_path):
    file = NamedTemporaryFile()
    yield Path(file.name)


@pytest.fixture
def eval_data():
    return page(results=[CheckResult(), CheckResult()])


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


def test_html_report(tmp_file, eval_data):
    output_file = tmp_file
    report.HTMLReport().render(eval_data, output_file)

    assert output_file.exists()


def test_pdf_report(tmp_file, eval_data):
    output_file = tmp_file
    report.PDFReport().render(eval_data, output_file)

    assert output_file.exists()
