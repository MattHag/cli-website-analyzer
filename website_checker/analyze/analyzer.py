import glob
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Any, Dict

from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import PageEvaluation
from website_checker.crawl.websitepage import WebsitePage

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

    def run_checks(self, page: WebsitePage):
        """Collects analyzer results for a single page."""
        page_result = PageEvaluation(url=page.url, title=page.title)
        for analyzer_class in self.__class__.registry.values():
            result = analyzer_class().check(page)
            if result:
                page_result.add_result(result)
                if result.tags:
                    page_result.set_tags(result.tags)
        return page_result
