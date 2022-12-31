from typing import List, Union

from website_checker.analyze.result import PageResult
from website_checker.check.cookies import CheckCookies
from website_checker.check.external_network_access import CheckExternalNetworkAccess
from website_checker.check.h1_headings import CheckH1Headings


class Analyzer:
    def __init__(self):
        self.registry = {}
        self._register_analyzer_classes()

    def _register_analyzer_classes(self):
        # TODO Retrieve analyzers dynamically
        classes = [CheckCookies, CheckExternalNetworkAccess, CheckH1Headings]
        for cls in classes:
            if cls.__name__ not in self.registry:
                self.registry[cls.__name__] = cls

    def run(self, page: Union[PageResult, List[PageResult]]):
        return self._evaluate(page)

    def _evaluate(self, page):
        """Runs all evaluations and collects the results."""
        page_result = PageResult(url=page.url, title=page.title)
        for analyzer_class in self.registry.values():
            result = analyzer_class().check(page)
            if result:
                page_result.add_evaluation(result.as_dict())
        return page_result
