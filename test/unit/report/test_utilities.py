import tempfile
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from website_checker.report import utilities


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
    content = b"""<div class="header">
        <h1>Website checker results</h1>
        <p class="header__title">{{ title }}</p>
        <div class="header__date">{{ creation_date }}</div>
    </div>"""
    html_template = tempfile.NamedTemporaryFile(delete=False)
    html_template.write(content)
    html_template.seek(0)
    yield Path(html_template.name)


def test_build_html(html_template):
    context = {
        "title": "Test",
        "creation_date": "2020-01-01",
    }
    html_string = utilities.build_html(html_template, context)

    assert html_string
    assert "Test" in html_string
    assert "2020-01-01" in html_string


def test_build_html_file(html_tmp_file, html_template):
    output_file = html_tmp_file
    context = {
        "title": "Test",
        "creation_date": "2020-01-01",
    }
    html_string = utilities.build_html(html_template, context, output_file)

    assert output_file.is_file()
    with open(output_file, "r") as f:
        content = f.read()
        assert content == html_string
        assert "Test" in html_string
        assert "2020-01-01" in html_string


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

    assert type(pdf_bytes) == bytes
    assert pdf_bytes[:4] == expected_pdf_signature


def test_html_to_pdf_file(html_bytes, html_tmp_file):
    expected_bytes = utilities.html_to_pdf(html_bytes, html_tmp_file)

    file_bytes = Path(html_tmp_file).read_bytes()

    assert Path(html_tmp_file).is_file()
    assert file_bytes == expected_bytes
