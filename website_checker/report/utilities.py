import contextlib
import shutil
import tempfile
from pathlib import Path
from typing import Protocol, Union

from jinja2 import Environment, FileSystemLoader
from playwright.async_api import PdfMargins
from playwright.sync_api import sync_playwright


class SupportsToDict(Protocol):
    def to_dict(self) -> dict:
        ...


def build_html(html_template: Union[str, Path], context: SupportsToDict, path: Union[None, str, Path] = None) -> str:
    """Converts HTML to PDF.

    Parameters
    ----------
    html_template
        The HTML template file with Jinja2 variables.
    context: SupportsToDict
        The context to render the HTML template with.
    path
        The path to save the rendered HTML file to. If not given, the HTML is not written to a file.

    Returns
    -------
    The rendered HTML source code.
    """
    html_template = Path(html_template)
    template_dir = html_template.parent
    template_name = html_template.name

    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template(template_name)
    html_string = template.render(context.to_dict())

    if path:
        with open(path, mode="w", encoding="utf-8") as results:
            results.write(html_string)
    return html_string


def _text_to_file(text: Union[bytes, str]) -> Path:
    """Returns a temporary file with given content."""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    if type(text) is str:
        text = bytes(text, encoding="utf-8")
    assert type(text) is bytes
    tmp_file.write(text)
    tmp_file.seek(0)
    # TODO close file
    return Path(tmp_file.name)


@contextlib.contextmanager
def ensure_html_extension_ctx(path: Path):
    """Ensures that the path is an .html file."""
    if path.suffix == ".html":
        yield path
    else:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        tmp_path = Path(tmp_file.name)
        shutil.copy(path, tmp_path)
        yield tmp_path
        tmp_file.close()


def html_to_pdf(html: Union[bytes, str, Path], path: Union[None, str, Path] = None) -> bytes:
    """Converts HTML to PDF.

    Parameters
    ----------
    html
        The HTML bytes or file to convert.
    path
        The path to save the PDF file to. If not given, the PDF is not written to a file.

    Returns
    -------
    The PDF file as bytes.
    """
    if type(html) is bytes:
        html = _text_to_file(html)
    elif type(html) is str:
        if Path(html).is_file():
            html = Path(html)
        else:
            html = _text_to_file(html)
    elif not isinstance(html, Path):
        raise TypeError(f"Unsupported type: {type(html)}")

    assert html.is_file()

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            with ensure_html_extension_ctx(html) as tmp_html_file:
                assert tmp_html_file.suffix == ".html"  # Playwright requires .html for rendering
                html_url = f"file://{str(tmp_html_file)}"
                page.goto(html_url)
                margin: PdfMargins = {"top": "2cm", "bottom": "2cm", "left": "2cm", "right": "2cm"}
                pdf_bytes = page.pdf(path=path, format="A4", margin=margin)
            return pdf_bytes
        finally:
            browser.close()
