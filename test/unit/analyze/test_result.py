import pytest

from website_checker.analyze.result import AnalyzerResult


@pytest.fixture
def analyzer_result():
    return AnalyzerResult(title="Example")


def test_result_with_title_dict(analyzer_result):
    expected_title = "Example result"

    result = AnalyzerResult(expected_title).as_dict()

    assert result is not None
    assert result["title"] == expected_title
    assert "description" not in result


def test_result_with_description_dict():
    expected_title = "Example result"
    expected_description = "Example description"

    result = AnalyzerResult(expected_title, expected_description).as_dict()

    assert result is not None
    assert result["title"] == expected_title
    assert result["description"] == expected_description


def test_add_elements_as_result(analyzer_result):
    expected_list = ["a", "b", "c"]

    for item in expected_list:
        analyzer_result.add_element(item)

    assert analyzer_result is not None
    assert analyzer_result.result == expected_list


def test_set_result(analyzer_result):
    expected_text = "This is the result"

    analyzer_result.set_result(expected_text)

    assert analyzer_result is not None
    assert analyzer_result.result == expected_text
