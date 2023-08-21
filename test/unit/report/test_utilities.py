import tempfile
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from website_checker.report import utilities
from website_checker.report.report_data import ReportData


@pytest.fixture
def html_bytes():
    yield b"""<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>"""


@pytest.fixture
def html_file(html_bytes):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    tmp_file.write(html_bytes)
    tmp_file.seek(0)
    yield Path(tmp_file.name)
    tmp_file.close()


@pytest.fixture
def html_tmp_file(tmp_path):
    file = NamedTemporaryFile(suffix=".html")
    yield Path(file.name)
    file.close()


@pytest.fixture
def html_template():
    content = b"""<div class="container header">
            <h1>Website report</h1>
            <p>{{ creation_date }}</p>
        </div>"""
    html_template = tempfile.NamedTemporaryFile(delete=False)
    html_template.write(content)
    html_template.seek(0)
    yield Path(html_template.name)


def test_build_html(html_template):
    context = ReportData(
        url="https://www.example.com",
    )
    html_string = utilities.build_html(html_template, context)

    assert html_string


def test_build_html_file(html_tmp_file, html_template):
    output_file = html_tmp_file
    context = ReportData(
        url="https://www.example.com",
    )
    html_string = utilities.build_html(html_template, context, output_file)

    assert output_file.is_file()
    with open(output_file, "r") as f:
        content = f.read()
        assert content == html_string


@pytest.mark.parametrize(
    "html_input",
    [
        "html_bytes",
        "html_file",
    ],
)
def test_html_to_pdf_bytes(html_input, request):
    expected_pdf_signature = b"%PDF"

    html = request.getfixturevalue(html_input)
    pdf_bytes = utilities.html_to_pdf(html)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:4] == expected_pdf_signature


def test_html_to_pdf_file(html_bytes, html_tmp_file):
    expected_bytes = utilities.html_to_pdf(html_bytes, html_tmp_file)

    file_bytes = Path(html_tmp_file).read_bytes()

    assert Path(html_tmp_file).is_file()
    assert file_bytes == expected_bytes
