import abc
from typing import List, Union

from website_checker.analyze.result import AnalyzerResult


class BaseAnalyzer(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def check(cls, page) -> Union[AnalyzerResult, List[AnalyzerResult]]:
        """Analyzes one page of a website and returns the results."""
        ...

    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseAnalyzer:
            attrs = set(dir(C))
            if set(cls.__abstractmethods__) <= attrs:
                return True
        return NotImplemented
