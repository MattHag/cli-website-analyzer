from pathlib import Path

from website_checker.analyze.analyzer import Analyzer
from website_checker.crawl.crawler import Crawler
from website_checker.report.report import Report


class WebsiteChecker:
    def __init__(self):
        self.analyzer = Analyzer()
        self.reporting = Report()

    def check(self, url) -> Path:
        with Crawler() as crawler:
            crawler.add_links(url)
            page = crawler.next()
        eval_list = self.analyzer.run(page)
        return self.reporting.create(eval_list)
