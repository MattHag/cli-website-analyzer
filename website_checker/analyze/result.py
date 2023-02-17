from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class Status(Enum):
    OK = "Okay"
    WARNING = "Warning"
    FAILED = "Failed"


class PageEvaluation:
    """Represents the analyzer results for a single URL."""

    def __init__(self, url: str, title: str, results=None):
        if results is None:
            results = []
        self.url = url
        self.title = title
        self.results = results

    def add_result(self, evaluation):
        self.results.append(evaluation)


class PageContextAdapter:
    def __call__(self, evaluated_pages: List[PageEvaluation]) -> Dict[str, Any]:
        """Adapts analyzer results to a context for report creation."""
        evaluated_pages.sort(key=lambda x: x.url)
        context = {
            "url": evaluated_pages[0].url,
            "creation_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "pages": evaluated_pages,
        }
        return context
