import pytest

from website_checker.check.detect_page_builder import DetectPageBuilder


@pytest.fixture
def wp_page_using_pagebuilder(page):
    """Returns a WordPress page using a page builder."""
    page.html = "<section><div class='brxe-asdf'>Section 1</div></section>"
    return page


def test_check_wordpress_detected(page):
    res = DetectPageBuilder().check(page)

    assert len(res.tags) == 1
    assert "WordPress" in res.tags


def test_check_pagebuilder(wp_page_using_pagebuilder):
    res = DetectPageBuilder().check(wp_page_using_pagebuilder)

    assert "Detect Page Builder" in res.title

    assert len(res.tags) == 2
    assert ["WordPress", "Bricks"] == res.tags
