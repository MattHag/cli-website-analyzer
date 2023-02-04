import urllib
from urllib.parse import ParseResult, urlparse

from website_checker.analyze import base_analyzer
from website_checker.analyze.result import AnalyzerResult


def is_internal_link(url: str, domain: str) -> bool:
    """Checks if url is an internal link."""
    if url.startswith(domain):
        len_domain = len(domain)
        if len(url) == len_domain:
            return True
        if url[len_domain] == "/":
            return True
    return False


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
            if not is_internal_link(resource.url, domain):
                res.add_element(resource.url)
        if not res.result:
            res.set_result("Nice, no external network access detected.")
        return res
