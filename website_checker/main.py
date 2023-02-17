from pathlib import Path
from typing import List

from website_checker.analyze.analyzer import Analyzer
from website_checker.analyze.result import PageContextAdapter, PageEvaluation
from website_checker.crawl.crawler import Crawler
from website_checker.crawl.websitepage import WebsitePage
from website_checker.report import report

PDF_OUTPUT = Path(__file__).parent.parent / "output" / "report.pdf"


class WebsiteChecker:
    def __init__(self, analyzer=None):
        if analyzer is None:
            analyzer = Analyzer()
        self.analyzer = analyzer

    def check(self, url) -> Path:
        crawled_pages = self.crawl(url)
        evaluation = self.evaluate(crawled_pages)
        return self.report(evaluation)

    def crawl(self, url) -> List[WebsitePage]:
        pages = []
        with Crawler(url) as crawler:
            for page in crawler:
                pages.append(page)
        return pages

    def evaluate(self, pages: List[WebsitePage]) -> List[PageEvaluation]:
        evaluated_data = []
        for page in pages:
            eval_result = self.analyzer.run_checks(page)
            evaluated_data.append(eval_result)
        return evaluated_data

    def report(self, evaluated_pages: List[PageEvaluation]):
        adapter = PageContextAdapter()
        context = adapter(evaluated_pages)
        return report.PDFReport().render(context, PDF_OUTPUT)
