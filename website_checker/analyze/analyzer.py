import glob
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Any, Dict, List, Union

from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import PageResult

check_dir = Path(__file__).parent.parent / "check"


def load_modules(package):
    """Loads all modules in a package."""
    for module in glob.glob(str(package / "**/*.py"), recursive=True):
        stem = Path(module).stem
        SourceFileLoader(stem, module).load_module()


class Analyzer:
    registry: Dict[str, Any] = {}

    def __init__(self):
        if not self.__class__.registry:
            load_modules(check_dir)
            classes = {cls.__name__: cls for cls in BaseAnalyzer.__subclasses__()}
            self.__class__.registry = classes

    def run(self, page: Union[PageResult, List[PageResult]]):
        return self._evaluate(page)

    def _evaluate(self, page):
        """Runs all evaluations and collects the results."""
        page_result = PageResult(url=page.url, title=page.title)
        for analyzer_class in self.__class__.registry.values():
            result = analyzer_class().check(page)
            if result:
                page_result.add_evaluation(result.as_dict())
        return page_result
