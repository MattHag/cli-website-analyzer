import base64
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
        self.tags: List[str] = []

    def add_result(self, evaluation):
        self.results.append(evaluation)

    def update_status(self):
        worst_status = sorted(self.results, key=lambda x: x.status.value, reverse=True)[0]
        self.status = Status(worst_status.status).name.lower()
        for entry in self.results:
            entry.res = Status(entry.status).name.lower()
        self.results.sort(key=lambda x: x.title)

    def set_tags(self, tags: List[str]):
        """Shows tags for this page."""
        self.tags = tags


class PageContextAdapter:
    def __call__(self, evaluated_pages: List[PageEvaluation], screenshot=None) -> Dict[str, Any]:
        """Adapts analyzer results to a context for report creation."""
        evaluated_pages = sort_by_url(evaluated_pages)
        sitemap_list = sort_by_url(evaluated_pages)

        summary = self.create_status_summary(evaluated_pages)
        descriptions = self.collect_test_descriptions(evaluated_pages)
        common_tags = collect_common_tags(evaluated_pages)

        for entry in summary:
            entry["status"] = Status(entry["status"]).name
        for page in evaluated_pages:
            page.update_status()
            for result in page.results:
                result.status = Status(result.status).name.lower()
            page.results.sort(key=lambda x: x.title)

        context = {
            "url": evaluated_pages[0].url,
            "creation_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "summary": summary,
            "sitemap": sitemap_list,
            "pages": evaluated_pages,
            "descriptions": descriptions,
        }
        if screenshot:
            screenshot_bytes = base64.b64encode(screenshot).decode()
            context.update({"screenshot": screenshot_bytes})
        if common_tags:
            context.update({"tags": common_tags})
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


def collect_common_tags(evaluated_pages: List[PageEvaluation]) -> List[str]:
    """Collects all tags that are present on all pages."""
    common_tags = []
    tags = list(set([tag for page in evaluated_pages for tag in page.tags]))
    for tag in tags:
        if all([tag in page.tags for page in evaluated_pages]):
            common_tags.append(tag)
    common_tags.sort()
    return common_tags


def sort_by_url(objects: list):
    """Sorts a list of objects by their url attribute.

    Any object with a url attribute can be used.
    """
    return sorted(objects, key=lambda page: (page.url.rstrip("/"), page))
