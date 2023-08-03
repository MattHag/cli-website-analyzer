from typing import List, Union

from website_checker.analyze.result import Status


class BaseAnalyzer:
    def __init__(self, hidden=False):
        self.hidden = hidden
        self.title = None
        self.description = None  # Text or HTML
        self.result = None
        self.status = None
        self.tags = []

    def check(self, page):
        """Analyzes one page of a website and sets the results."""
        raise NotImplementedError

    def save_result(self, data, status: Status):
        """Sets result as ."""
        if self.result is None:
            self.result = {}
        if isinstance(data, list):
            self.result.update(
                {
                    "list": {"entries": data},
                }
            )
        if isinstance(data, dict):
            if "heading" in data:
                self.result.update(
                    {
                        "table": {"heading": data["heading"], "entries": data["entries"]},
                    }
                )
            else:
                self.result.update(
                    {
                        "table": {"entries": data["entries"]},
                    }
                )
        if type(data) == str:
            self.result.update({"text": data})

        self._set_status(status)

    def _set_status(self, status: Status):
        """Updates status if new one is worse."""
        if self.status is None:
            self.status = status
        elif status > self.status:
            self.status = status

    def add_tags(self, tags: Union[str, List[str]]):
        """Adds tags to the result."""
        if isinstance(tags, str):
            tags = [tags]
        if len(tags) == 0:
            raise ValueError("No tag given.")
        self.tags += tags

    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseAnalyzer:
            attrs = set(dir(C))
            if set(cls.__abstractmethods__) <= attrs:
                return True
        return NotImplemented
