import pytest

from website_checker.analyze.result import (
    PageEvaluation,
    Result,
    Status,
    collect_test_descriptions,
    create_status_summary,
)


def _create_result(status=Status.OK):
    return Result(
        title="Test Result",
        description="Description of a test",
        result={"text": "This is a test result"},
        status=status,
    )


@pytest.fixture
def mock_eval_pages():
    pages = [
        PageEvaluation(
            url="test1.com",
            title="Testpage 1",
            results=[_create_result()],
        ),
        PageEvaluation(
            url="test2.com",
            title="Testpage 2",
            results=[_create_result(Status.WARNING)],
        ),
    ]
    yield pages


def test_collect_test_descriptions(mock_eval_pages):
    expected_unique_tests = 1
    res = collect_test_descriptions(mock_eval_pages)

    assert len(res) == expected_unique_tests
    assert res[0].title == "Test Result"
    assert res[0].description == "Description of a test"


def test_create_status_summary(mock_eval_pages):
    expected_pages = 1
    res = create_status_summary(mock_eval_pages)

    assert len(res) == expected_pages
    assert res[0].title == "Test Result"
    assert res[0].status == Status.WARNING
