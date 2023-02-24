from website_checker.check.external_network_access import CheckExternalNetworkAccess
from website_checker.crawl.resource import Resource, ResourceRequest
from website_checker.crawl.websitepage import WebsitePage


def test_check_external_network_access():
    domain = "https://local.url"
    external = [
        Resource(url="https://www.googletagmanager.com/gtag/js?id=UA-1234567"),
        Resource(url="https://fonts.googleapis.com/css?family=Tangerine"),
        Resource(url=f"{domain}.testdomain.url/content/image.jpg"),
    ]
    resources = external + [
        Resource(url=f"{domain}/content/image.jpg"),
    ]
    page = WebsitePage(url=domain, title="Testsite", elements=resources, html="")

    res = CheckExternalNetworkAccess().check(page)

    assert "external network access" in res.title.lower()
    assert len(res.result["list"]["entries"]) == len(external)


def test_check_failed_external_request():
    domain = "https://local.url"
    external_url = "https://externaldomain.url/blog/hello_world"
    failed_requests = [ResourceRequest(url=external_url, failure="DNS lookup failed")]
    page = WebsitePage(url=domain, title="Testsite", failed_requests=failed_requests)

    res = CheckExternalNetworkAccess().check(page)

    assert "external network access" in res.title.lower()
    assert len(res.result["list"]["entries"]) == 1
    assert external_url in res.result["list"]["entries"][0]


def test_check_no_external_network_access():
    domain = "https://local.url"
    resources = [
        Resource(url=f"{domain}/blog/hello_world"),
        Resource(url=f"{domain}/blog/hello_world_2"),
    ]
    failed_requests = [ResourceRequest(url=f"{domain}/blog/hello_world_3", failure="DNS lookup failed")]
    page = WebsitePage(url=domain, title="Testsite", elements=resources, failed_requests=failed_requests)

    res = CheckExternalNetworkAccess().check(page)

    assert "no external network access" in res.result["text"].lower()
