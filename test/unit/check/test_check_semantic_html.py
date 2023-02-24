from website_checker.analyze.result import Status
from website_checker.check.semantic_html import CheckSemanticHtml


def test_check_semantic_html(page):
    expected = "header (1), main (1), section (2)"
    page.html = (
        "<header></header><main>   <section><div>Section 1</div></section>   <section>Section 2</section></main>"
    )
    res = CheckSemanticHtml().check(page)

    assert "semantic html" in res.title.lower()
    assert "checks usage of structural semantic" in res.description.lower()

    assert res.status == Status.OK
    assert "structural semantic tags are used" in res.result["text"].lower()
    assert expected in res.result["text"].lower()


def test_check_no_semantic_html(page):
    page.html = ""
    res = CheckSemanticHtml().check(page)

    assert res.status == Status.WARNING
    assert "no structural semantic tags" in res.result["text"].lower()
