from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class Status(Enum):
    OK = 1
    WARNING = 2
    FAILED = 3


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

        summary = self.create_status_summary(evaluated_pages)
        descriptions = self.collect_test_descriptions(evaluated_pages)
        for entry in summary:
            entry["status"] = Status(entry["status"]).name
        for page in evaluated_pages:
            for result in page.results:
                result.status = Status(result.status).name.lower()
            page.results.sort(key=lambda x: x.title)

        context = {
            "url": evaluated_pages[0].url,
            "creation_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "summary": summary,
            "pages": evaluated_pages,
            "descriptions": descriptions,
        }
        return context

    def collect_test_descriptions(self, evaluated_pages):
        descriptions = {}
        for page in evaluated_pages:
            for result in page.results:
                if result.description:
                    descriptions[result.title] = result.description
        return sorted(descriptions.items(), key=lambda x: x[0])

    def create_status_summary(self, evaluated_pages):
        test_summary = {}
        for page in evaluated_pages:
            for result in page.results:
                entry = test_summary.get(
                    result.title,
                    {"title": result.title, "status": result.status},
                )
                if result.status > entry["status"]:
                    entry["status"] = result.status
                test_summary[result.title] = entry
        return sorted(test_summary.values(), key=lambda x: x["title"])
