from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import Status


class CheckCookies(BaseAnalyzer):
    def check(self, page):
        self.title = "Cookie without consent"
        self.description = "Shows cookies, that are set without consent."

        found_cookies = []
        for cookie in page.cookies:
            # TODO Add additional information for cookies
            found_cookies.append(cookie.name)

        if found_cookies:
            self.save_result(found_cookies, Status.WARNING)
        else:
            self.save_result("Well done, no cookies set without prior consent.", Status.OK)
        return self
