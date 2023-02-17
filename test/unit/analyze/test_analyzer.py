import abc
from unittest import mock

import pytest

from website_checker.analyze.analyzer import Analyzer
from website_checker.analyze.base_analyzer import BaseAnalyzer


class InvalidClass(metaclass=abc.ABCMeta):
    pass


class TestAnalyzer(BaseAnalyzer):
    def check(self, page):
        pass


def test_register_analyzers():
    analyzer = Analyzer()

    assert TestAnalyzer in analyzer.registry.values()
    assert InvalidClass not in analyzer.registry.values()


def test_run_analyzer(page):
    analyzer = Analyzer()

    result = analyzer.run_checks(page)

    assert result


# parametrize
@pytest.mark.parametrize(
    "input, expected_result",
    [
        ("This is a result.", {"text": "This is a result."}),
        (["col1", "col2"], {"list": ["col1", "col2"]}),
    ],
)
def test_base_analyzer_save_result_text(input, expected_result):
    analyzer = TestAnalyzer()

    analyzer.save_result(input, mock.Mock())

    assert analyzer.result == expected_result
