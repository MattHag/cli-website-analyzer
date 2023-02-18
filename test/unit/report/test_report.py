from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from website_checker.analyze.result import PageContextAdapter, PageEvaluation, Status
from website_checker.report import report

DEFAULT_HTML_OUTPUT = Path(__file__).parent.parent.parent.parent / "output" / "report.html"


@pytest.fixture
def tmp_file(tmp_path):
    file = NamedTemporaryFile(suffix=".html", dir="/tmp")
    file.name = tmp_path / "test.html"
    yield Path(file.name)
    file.close()


class Result:
    def __init__(self, title="Test Result"):
        self.title = title
        self.description = "This is a test result"
        self.result = {"list": {"entries": ["_ga", "_gid"]}}
        self.status = Status.WARNING.value


def page(title="Example", results=None):
    if results is None:
        results = []
    return PageEvaluation(
        url="https://www.example.com",
        title=title,
        results=results,
    )


@pytest.fixture
def eval_pages():
    return [page(results=[Result(), Result()])]


@pytest.fixture
def adapted_context(eval_pages):
    adapter = PageContextAdapter()
    return adapter(eval_pages)


def test_html_report_jinja(tmp_file, adapted_context):
    output_file = tmp_file
    report.HTMLReport().render(adapted_context, output_file)

    assert output_file.exists()


def test_pdf_report_jinja(tmp_file, adapted_context):
    output_file = tmp_file
    report.PDFReport().render(adapted_context, output_file)

    assert output_file.exists()


def test_adapter(eval_pages):
    adapter = PageContextAdapter()
    context = adapter(eval_pages)

    assert len(context["pages"][0].results) == 2


def test_html_report_using_adapter(tmp_file, eval_pages):
    output_file = tmp_file

    adapter = PageContextAdapter()
    context = adapter(eval_pages)
    report.HTMLReport().render(context, output_file)

    assert output_file.exists()


def test_pdf_report_using_adapter(tmp_file, eval_pages):
    output_file = tmp_file

    adapter = PageContextAdapter()
    context = adapter(eval_pages)
    report.PDFReport().render(context, output_file)

    assert output_file.exists()
