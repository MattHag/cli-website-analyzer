from website_checker.analyze.analyzer import Analyzer


def test_analyzer(page):
    analyzer = Analyzer()

    result = analyzer.run(page)

    assert result
