import os
import tempfile
from pathlib import Path

from website_checker.report import utilities

DEFAULT_TEMPLATE = Path(__file__).parent / "templates" / "base_template.html"

DEBUG = False
if os.environ.get("DEBUG"):
    DEBUG = True

DEFAULT_OUTPUT_PATH = Path(__file__).parent.parent.parent / "output"
DEFAULT_HTML_OUTPUT = DEFAULT_OUTPUT_PATH / "report.html"


class ReportTemplate:
    def __init__(self, html_template=DEFAULT_TEMPLATE):
        self.html_template = html_template

    def render(self, data, path: Path):
        raise NotImplementedError


class HTMLReport(ReportTemplate):
    def render(self, data, html_path: Path) -> Path:
        """Builds an HTML report from the given data."""
        if DEBUG:
            html_path = DEFAULT_HTML_OUTPUT
        utilities.build_html(self.html_template, data, html_path)
        return html_path


class PDFReport(HTMLReport):
    def render(self, data, path: Path) -> Path:
        """Builds a PDF report from the given data."""
        with tempfile.NamedTemporaryFile() as tmp_file:
            html = super().render(data, Path(tmp_file.name))
            utilities.html_to_pdf(html, path)
        return path
