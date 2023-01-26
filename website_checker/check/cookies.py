from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import Status
from website_checker.check.cookies_data.cookie_database import CookieDatabase


class CheckCookies(BaseAnalyzer):
    def check(self, page):
        self.title = "Cookies without consent"
        self.description = "Finds cookies, that are stored without user consent."

        allowed_keys = {
            "cookie_name",
            "platform",
            "retention_period",
            "category",
        }
        cookies = []
        with CookieDatabase() as cookie_db:
            for cookie in page.cookies:
                result = cookie_db.search(cookie.name)
                if result:
                    cookie_details = {key: result[key] for key in result if key in allowed_keys}
                    cookies.append(cookie_details)
                else:
                    cookies.append({"cookie_name": cookie.name})
            if cookies:
                headings = [heading.replace("_", " ").capitalize() for heading in cookies[0].keys()]
                cookies = [list(cookie.values()) for cookie in cookies]
                self.save_result({"heading": headings, "entries": cookies}, Status.WARNING)
            else:
                self.save_result("Well done, no cookies set without user consent.", Status.OK)
            return self
