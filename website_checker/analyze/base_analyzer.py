from typing import Any

from website_checker.analyze.result import Status


class BaseAnalyzer:
    def __init__(self):
        self.title: str = None
        self.description: str = None
        self.result: Any = None
        self.status: str = None

    def check(self, page):
        """Analyzes one page of a website and sets the results."""
        raise NotImplementedError

    def save_result(self, data, status: Status):
        """Sets result as ."""
        if isinstance(data, list):
            self.result = {"list": data}
        else:
            self.result = {"text": data}
        self.status = status.value

    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseAnalyzer:
            attrs = set(dir(C))
            if set(cls.__abstractmethods__) <= attrs:
                return True
        return NotImplemented
