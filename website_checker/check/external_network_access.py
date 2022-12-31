import urllib
from urllib.parse import ParseResult, urlparse

from website_checker.analyze import base_analyzer
from website_checker.analyze.result import AnalyzerResult


def get_base_domain(url: str) -> str:
    parts = urlparse(url)
    return urllib.parse.urlunparse(
        ParseResult(
            scheme=parts.scheme,
            netloc=parts.netloc,
            path="",
            params="",
            query="",
            fragment="",
        )
    )


class CheckExternalNetworkAccess(base_analyzer.BaseAnalyzer):
    def check(self, page):
        domain = get_base_domain(page.url)

        res = AnalyzerResult(
            title="External network access",
            description="Searches for network access to external servers.",
        )
        for resource in page.elements:
            if not resource.url.startswith(domain):
                res.add_element(resource.url)
        if not res.result:
            res.set_result("Nice, no external network access detected.")
        return res
