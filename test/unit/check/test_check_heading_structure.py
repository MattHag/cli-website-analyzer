import pytest

from website_checker.analyze.result import Status
from website_checker.check.heading_structure import (
    CheckHeadingStructure,
    next_allowed_heading,
)


@pytest.mark.parametrize(
    "last_heading,expected_next",
    [
        (None, ["h1"]),
        ("h1", ["h2"]),
        ("h2", ["h2", "h3"]),
        ("h3", ["h2", "h3", "h4"]),
        ("h4", ["h2", "h3", "h4", "h5"]),
        ("h5", ["h2", "h3", "h4", "h5", "h6"]),
        ("h6", ["h2", "h3", "h4", "h5", "h6"]),
    ],
)
def test_next_allowed_heading(last_heading, expected_next):
    res = next_allowed_heading(last_heading)

    assert res == expected_next


def test_single_h1_heading(page):
    res = CheckHeadingStructure().check(page)

    assert "heading structure" in res.title.lower()
    assert res.status == Status.OK.value
    assert res.result["text"]


def test_multiple_h1_headings(page):
    expected_result = "First H1 Heading"
    page.html = f"<h1>{expected_result}</h1><h1>Second H1 Heading</h1>"

    res = CheckHeadingStructure().check(page)

    assert res.status == Status.WARNING.value
    assert len(res.result["list"]["entries"]) == 2


def test_complex_tree(page):
    page.html = "<h1>Single H1 Heading</h1><h2>Heading 2</h2><h3>Heading 3</h3><h2>Second H2</h2>"

    res = CheckHeadingStructure().check(page)

    assert res.status == Status.OK.value
    assert res.result["text"]


def test_missing_h1(page):
    page.html = ""
    res = CheckHeadingStructure().check(page)

    assert res.status == Status.WARNING.value
    assert "no heading" in res.result["text"].lower()


def test_invalid_h2_before_h1(page):
    page.html = "<h2>First heading</h2><h1>Second heading</h1>"
    res = CheckHeadingStructure().check(page)

    assert res.status == Status.WARNING.value
    assert "expected one of h1" in res.result["text"].lower()
    assert len(res.result["list"]["entries"]) == 1
