from pathlib import Path

from website_checker.analyze.analyzer import Analyzer
from website_checker.crawl.crawler import Crawler
from website_checker.report import report

PDF_OUTPUT = Path(__file__).parent.parent / "output" / "report.pdf"


class WebsiteChecker:
    def __init__(self):
        self.analyzer = Analyzer()

    def check(self, url) -> Path:
        eval_list = []
        with Crawler(url) as crawler:
            for page in crawler:
                eval_result = self.analyzer.run(page)
                eval_list.append(eval_result)
        eval_list.sort(key=lambda x: x.url)
        return report.PDFReport().render(eval_list, PDF_OUTPUT)
