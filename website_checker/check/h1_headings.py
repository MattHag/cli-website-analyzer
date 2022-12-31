from bs4 import BeautifulSoup

from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import AnalyzerResult


class CheckH1Headings(BaseAnalyzer):
    def check(self, page):
        res = AnalyzerResult(
            title="H1 Headings",
            description="Checks existence of at least one H1 heading.",
        )

        soup = BeautifulSoup(page.html, "html.parser")
        headings = soup.find_all("h1")
        if len(headings) == 1:
            res.set_result(f"Great, one H1 heading '{headings[0].text}' found.")
        elif len(headings) >= 2:
            res.set_result(f"Multiple H1 headings found, first one is '{headings[0].text}'.")
        else:
            res.set_result("Warning, no H1 heading found.")
        return res
