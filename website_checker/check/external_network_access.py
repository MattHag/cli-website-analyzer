import urllib
from urllib.parse import ParseResult, urlparse

from website_checker.analyze import base_analyzer
from website_checker.analyze.result import Status


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
        self.title = "External network access"
        self.description = "Searches for network access to external servers."

        domain = get_base_domain(page.url)

        external_resources = []
        for resource in page.elements:
            if not is_internal_link(resource.url, domain):
                external_resources.append(resource.url)

        if external_resources:
            self.save_result(external_resources, Status.WARNING)
        else:
            self.save_result("Nice, no external network access detected.", Status.OK)
        return self
