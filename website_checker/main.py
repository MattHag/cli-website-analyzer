from pathlib import Path

from website_checker.analyze.analyzer import Analyzer
from website_checker.crawl.crawler import Crawler
from website_checker.report.report import Report


class WebsiteChecker:
    def __init__(self):
        self.analyzer = Analyzer()
        self.reporting = Report()

    def check(self, url) -> Path:
        eval_list = []
        with Crawler(url) as crawler:
            for page in crawler:
                eval_result = self.analyzer.run(page)
                eval_list.append(eval_result)
        eval_list.sort(key=lambda x: x.url)
        return self.reporting.create(eval_list)
