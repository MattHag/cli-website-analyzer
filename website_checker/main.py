import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Protocol, Tuple

from website_checker import utils
from website_checker.analyze.result import PageEvaluation
from website_checker.crawl.browser import Browser
from website_checker.crawl.crawler import Crawler
from website_checker.crawl.websitepage import WebsitePage
from website_checker.report import report as report_util
from website_checker.report.report_data import ReportData

DEBUG = False
if os.environ.get("DEBUG"):
    DEBUG = True

DEFAULT_OUTPUT_PATH = Path(__file__).parent.parent / "output"
DEFAULT_PDF_OUTPUT = DEFAULT_OUTPUT_PATH / "report.pdf"


class SupportsRunChecks(Protocol):
    def run_checks(self, page: WebsitePage) -> PageEvaluation:
        ...


def run_full_analysis(
    url,
    analyzer: SupportsRunChecks,
    converter: Callable[[List[PageEvaluation]], ReportData],
    rate_limit=None,
    max_pages=None,
    save_crawled_pages=False,
) -> Tuple[Path, List[PageEvaluation], List[WebsitePage]]:
    creation_datetime = _make_creation_datetime()
    domainname = utils.get_domain_as_text(url)
    max_pages_option = f"{max_pages}p" if max_pages else "full"

    crawled_pages = crawl(
        url,
        rate_limit=rate_limit,
        max_pages=max_pages,
        save_data=save_crawled_pages,
    )

    evaluation_result = evaluate(analyzer, crawled_pages)

    report_filename = "_".join(["Report", max_pages_option, domainname, f"{creation_datetime}.pdf"])
    pdf_path = report(report_filename, evaluation_result, converter)
    return pdf_path, evaluation_result, crawled_pages


def crawl(url, rate_limit=False, max_pages=False, save_data=False) -> List[WebsitePage]:
    pages = []
    browser = Browser(rate_limit=rate_limit)
    with Crawler(browser, url) as crawler:
        for idx, page in enumerate(crawler, start=1):
            pages.append(page)
            if max_pages and idx >= max_pages:
                break
    if save_data:
        pickle.dump(pages, open(utils.get_desktop_path() / "pages.p", "wb"))
    return pages


def evaluate(analyzer: SupportsRunChecks, pages: List[WebsitePage]) -> List[PageEvaluation]:
    evaluated_data = []
    for page in pages:
        eval_result = analyzer.run_checks(page)
        evaluated_data.append(eval_result)
    return evaluated_data


def report(filename, evaluated_pages: List[PageEvaluation], converter: Callable):
    pdf_path = utils.get_desktop_path() / filename
    if DEBUG:
        pdf_path = DEFAULT_PDF_OUTPUT

    context = converter(evaluated_pages)
    return report_util.PDFReport().render(context, pdf_path)


def _make_creation_datetime():
    current_datetime = datetime.now()
    return utils.datetime_str(current_datetime).replace(" ", "_")
