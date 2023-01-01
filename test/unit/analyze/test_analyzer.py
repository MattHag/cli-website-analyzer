import abc

from website_checker.analyze.analyzer import Analyzer
from website_checker.analyze.base_analyzer import BaseAnalyzer


class InvalidClass(metaclass=abc.ABCMeta):
    pass


class TestAnalyzer(BaseAnalyzer):
    @classmethod
    def check(cls, page):
        pass


def test_register_analyzers():
    analyzer = Analyzer()

    assert TestAnalyzer in analyzer.registry.values()
    assert InvalidClass not in analyzer.registry.values()


def test_run_analyzer(page):
    analyzer = Analyzer()

    result = analyzer.run(page)

    assert result
