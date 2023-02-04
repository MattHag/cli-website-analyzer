import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from website_checker.report import utilities

DEFAULT_TEMPLATE = Path(__file__).parent / "templates" / "base_template.html"
DEFAULT_PDF_OUTPUT = Path(__file__).parent.parent.parent / "output" / "report.pdf"
DEFAULT_HTML_OUTPUT = Path(__file__).parent.parent.parent / "output" / "report.html"


class PageToContextAdapter:
    def __call__(self, page_eval) -> dict:
        """Creates a context for the report."""
        if type(page_eval) is not list:
            page_eval = [page_eval]

        return {
            "title": urlparse(page_eval[0].url).netloc,
            "creation_date": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "pages": page_eval,
        }


class ReportTemplate:
    def __init__(self, html_template=DEFAULT_TEMPLATE):
        self.html_template = html_template

    def render(self, data, path: Path):
        raise NotImplementedError


class HTMLReport(ReportTemplate):
    def render(self, data, path: Path) -> Path:
        """Builds an HTML report from the given data."""
        adapter = PageToContextAdapter()
        context = adapter(data)
        utilities.build_html(self.html_template, context, path)
        return path


class PDFReport(HTMLReport):
    def render(self, data, path: Path) -> Path:
        """Builds a PDF report from the given data."""
        with tempfile.NamedTemporaryFile() as tmp_file:
            html = super().render(data, Path(tmp_file.name))
            utilities.html_to_pdf(html, path)
        return path
