from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import AnalyzerResult


class CheckCookies(BaseAnalyzer):
    def check(self, page):
        res = AnalyzerResult(
            title="Cookie without consent",
            description="The following cookies are set without consent.",
        )
        for cookie in page.cookies:
            # TODO Add additional information for cookies
            res.add_element(cookie.name)
        if not res.result:
            res.set_result("Well done, no cookies set without prior consent.")
        return res
