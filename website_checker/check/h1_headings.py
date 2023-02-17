from bs4 import BeautifulSoup

from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import Status


class CheckH1Headings(BaseAnalyzer):
    def check(self, page):
        self.title = "H1 Headings"
        self.description = "Checks existence of at least one H1 heading."

        soup = BeautifulSoup(page.html, "html.parser")
        headings = soup.find_all("h1")
        if len(headings) == 1:
            self.save_result(f"Great, one H1 heading '{headings[0].text}' found.", Status.OK)
        elif len(headings) >= 2:
            self.save_result(f"Multiple H1 headings found, first one is '{headings[0].text}'.", Status.WARNING)
        else:
            self.save_result("Warning, no H1 heading found.", Status.FAILED)
        return self
