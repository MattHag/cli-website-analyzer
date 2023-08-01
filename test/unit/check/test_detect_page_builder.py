import pytest

from website_checker.check.detect_page_builder import DetectCMSPageBuilder
from website_checker.crawl.resource import Resource


@pytest.mark.parametrize(
    "url, expected_tags",
    [
        (
            "https://domain.test/wp-content/themes/notheme/assets/css/style.css?ver=1.0.0",
            ["WordPress"],
        ),
        (
            "https://domain.test/typo3temp/assets/typo3.html",
            ["TYPO3"],
        ),
        (
            "https://domain.test/sites/default/files/image.jpg",
            ["Drupal"],
        ),
        (
            "https://domain.test/shopifycloud/shopify/assets/shopify_pay/storefront-c31a21da2.js",
            ["Shopify"],
        ),
    ],
)
def test_check_resource_path(minimal_page, url, expected_tags):
    minimal_page.elements = [Resource(url=url)]

    res = DetectCMSPageBuilder().check(minimal_page)

    assert res.tags == expected_tags


@pytest.mark.parametrize(
    "meta_tag, expected_tags",
    [
        (
            '<meta name="generator" content="WordPress 6.2.1">',
            ["WordPress"],
        ),
        (
            '<meta name="generator" content="TYPO3 CMS">',
            ["TYPO3"],
        ),
        (
            '<meta name="Generator" content="Drupal 8 (https://www.drupal.org)">',
            ["Drupal"],
        ),
        (
            '<meta name="generator" content="Drupal 9 (https://www.drupal.org)">',
            ["Drupal"],
        ),
        (
            '<meta name="generator" content="Joomla! - Open Source Content Management">',
            ["Joomla"],
        ),
    ],
)
def test_check_meta_generator(minimal_page, meta_tag, expected_tags):
    minimal_page.html = f"<head>{meta_tag}></head><body></body>"

    res = DetectCMSPageBuilder().check(minimal_page)

    assert res.tags == expected_tags


def test_check_cms_and_pagebuilder(minimal_page):
    minimal_page.html = (
        '<head><meta name="generator" content="WordPress 6.2.1"></head>'
        '<section><div class="brxe-asdf">Section 1</div></section>'
    )
    res = DetectCMSPageBuilder().check(minimal_page)

    assert "Detect CMS and Page Builder" in res.title

    assert len(res.tags) == 2
    assert res.tags == ["WordPress", "Bricks"]
