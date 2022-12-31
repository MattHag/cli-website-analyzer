import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_').replace('.', '-')
    return re.sub(r'(?u)[^-\w.]', '', s)


root = Path(__file__).parent.parent.parent

template_dir = Path(__file__).parent / "templates"
environment = Environment(loader=FileSystemLoader(template_dir))


class Report:
    def __init__(self, report_filename="report"):
        self.report_filename = report_filename
        self.output_dir = Path(root / "output")

    def create(self, evaluation) -> Path:
        context = self.create_context(evaluation)
        html_file = self.render_html(context)
        return self.render_pdf(html_file)

    @staticmethod
    def create_context(page_eval) -> dict:
        if type(page_eval) is not list:
            page_eval = [page_eval]

        return {
            "title": urlparse(page_eval[0].url).netloc,
            "creation_date": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "pages": page_eval,
        }

    def render_html(self, context, template=None) -> Path:
        if not template:
            template = "base_template.html"
        results_template = environment.get_template(template)

        output_file = self.output_dir / f"{self.report_filename}.html"
        with open(output_file, mode="w", encoding="utf-8") as results:
            results.write(results_template.render(context))
            print(f"... wrote {output_file}")
        return output_file

    def render_pdf(self, html_file) -> Path:
        pdf_filename = self.output_dir / f"{get_valid_filename(self.report_filename)}.pdf"
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"file://{html_file}")
            page.pdf(path=pdf_filename)
            browser.close()
        return pdf_filename
