from website_checker.check.external_network_access import CheckExternalNetworkAccess
from website_checker.crawl.resource import Resource
from website_checker.crawl.websitepage import WebsitePage


def test_check_external_network_access():
    domain = "https://local.url"
    resources = [
        Resource(url="https://www.googletagmanager.com/gtag/js?id=UA-1234567"),
        Resource(url=f"{domain}/blog/hello_world"),
        Resource(url="https://fonts.googleapis.com/css?family=Tangerine"),
    ]

    expected_nr_results = len(resources) - 1
    page = WebsitePage(url=domain, elements=resources)

    res = CheckExternalNetworkAccess().check(page)

    assert "external network access" in res.title.lower()
    assert len(res.result) == expected_nr_results
    for resource in res.result:
        assert not resource.startswith(domain)


def test_check_no_external_network_access():
    domain = "https://local.url"
    resources = [
        Resource(url=f"{domain}/blog/hello_world"),
        Resource(url=f"{domain}/blog/hello_world_2"),
    ]
    page = WebsitePage(url=domain, elements=resources)

    res = CheckExternalNetworkAccess().check(page)

    assert "no external network access" in res.result.lower()
