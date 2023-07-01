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
        self.status = None  # worst status of all results

    def add_result(self, evaluation):
        self.results.append(evaluation)

    def update_status(self):
        worst_status = sorted(self.results, key=lambda x: x.status.value, reverse=True)[0]
        self.status = Status(worst_status.status).name.lower()


class PageContextAdapter:
    def __call__(self, evaluated_pages: List[PageEvaluation]) -> Dict[str, Any]:
        """Adapts analyzer results to a context for report creation."""
        evaluated_pages.sort(key=lambda x: x.url)

        summary = self.create_status_summary(evaluated_pages)
        descriptions = self.collect_test_descriptions(evaluated_pages)
        for entry in summary:
            entry["status"] = Status(entry["status"]).name
        for page in evaluated_pages:
            page.update_status()
            for result in page.results:
                result.status = Status(result.status).name.lower()
            page.results.sort(key=lambda x: x.title)

        sitemap_list = sort_by_url(evaluated_pages)

        context = {
            "url": evaluated_pages[0].url,
            "creation_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "summary": summary,
            "sitemap": sitemap_list,
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
                    {"title": result.title, "status": result.status.value},
                )
                result_value = result.status.value
                if result_value > entry["status"]:
                    entry["status"] = result_value
                test_summary[result.title] = entry
        return sorted(test_summary.values(), key=lambda x: x["title"])


def sort_by_url(objects: list):
    """Sorts a list of objects by their url attribute.

    Any object with a url attribute can be used.
    """
    return sorted(objects, key=lambda page: (page.url.rstrip("/"), page))
