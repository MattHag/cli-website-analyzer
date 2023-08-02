import os

from website_checker import main
from website_checker.analyze.analyzer import Analyzer

DEBUG = False
if os.environ.get("DEBUG"):
    DEBUG = True


def test_integrationtest(test_server, mock_desktop_path):
    url = test_server
    expected_pdf_signature = b"%PDF"

    analyzer = Analyzer()
    website_checker = main.WebsiteChecker(analyzer)
    pdf_file = website_checker.check(url, current_datetime=None)
    page_evaluations = website_checker.evaluation_result

    assert len(page_evaluations) == 2
    first_page = page_evaluations[0]

    assert all(page.screenshot is not None for page in page_evaluations)
    assert all(page.status == "ok" for page in page_evaluations)
    for test in first_page.results:
        if "total page size" in test.title.lower():
            assert " 0.0 " not in test.result["text"]
        if "resource load error" in test.title.lower():
            assert "0 requests are made" not in test.result["text"]
    assert pdf_file.is_file()
    file_bytes = pdf_file.read_bytes()
    assert file_bytes.startswith(expected_pdf_signature)

    if DEBUG:
        pdf_file.rename(main.DEFAULT_OUTPUT_PATH / "test_integrationtest.pdf")
