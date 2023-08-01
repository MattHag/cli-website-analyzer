import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple

from website_checker import utils
from website_checker.analyze.analyzer import Analyzer
from website_checker.analyze.result import PageContextAdapter, PageEvaluation
from website_checker.crawl.browser import Browser
from website_checker.crawl.crawler import Crawler
from website_checker.crawl.websitepage import WebsitePage
from website_checker.report import report

DEBUG = False
if os.environ.get("DEBUG"):
    DEBUG = True

DEFAULT_OUTPUT_PATH = Path(__file__).parent.parent / "output"
DEFAULT_PDF_OUTPUT = DEFAULT_OUTPUT_PATH / "report.pdf"


class WebsiteChecker:
    def __init__(self, analyzer=None, rate_limit=None, max_pages=None, save_crawled_pages=False):
        if analyzer is None:
            analyzer = Analyzer()
        self.analyzer = analyzer
        self.rate_limit = rate_limit
        self.max_pages = max_pages
        self.save_crawled_pages = save_crawled_pages

        self.filename = None
        self.creation_date = None
        self.evaluation_result = None

    def check(self, url, current_datetime=None) -> Path:
        if current_datetime is None:
            current_datetime = datetime.now()
        self.creation_date = utils.datetime_str(current_datetime).replace(" ", "_")
        domainname = utils.get_domain_as_text(url)
        max_pages_option = f"{self.max_pages}p" if self.max_pages else "full"
        self.filename = "_".join(["Report", max_pages_option, domainname, f"{self.creation_date}.pdf"])
        crawled_pages, screenshot = self.crawl(url)
        self.evaluation_result = self.evaluate(crawled_pages)
        return self.report(self.evaluation_result, screenshot)

    def crawl(self, url) -> Tuple[List[WebsitePage], Any]:
        pages = []
        browser = Browser(rate_limit=self.rate_limit)
        with Crawler(browser, url) as crawler:
            for idx, page in enumerate(crawler, start=1):
                pages.append(page)
                if self.max_pages and idx >= self.max_pages:
                    break
            screenshot_buffer = crawler.screenshot_encoded
        if self.save_crawled_pages:
            pickle.dump(pages, open(utils.get_desktop_path() / "pages.p", "wb"))
        return pages, screenshot_buffer

    def evaluate(self, pages: List[WebsitePage]) -> List[PageEvaluation]:
        evaluated_data = []
        for page in pages:
            eval_result = self.analyzer.run_checks(page)
            evaluated_data.append(eval_result)
        return evaluated_data

    def report(self, evaluated_pages: List[PageEvaluation], screenshot=None):
        pdf_path = utils.get_desktop_path() / self.filename
        if DEBUG:
            pdf_path = DEFAULT_PDF_OUTPUT

        adapter = PageContextAdapter()
        context = adapter(evaluated_pages, screenshot)
        return report.PDFReport().render(context, pdf_path)
