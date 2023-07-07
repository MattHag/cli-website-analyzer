import base64
from enum import Enum

from website_checker.analyze import base_analyzer
from website_checker.analyze.result import Status


class Impact(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SERIOUS = "serious"
    CRITICAL = "critical"


class CheckAccessibility(base_analyzer.BaseAnalyzer):
    def check(self, page):
        self.title = "Automated accessibility checks"
        self.description = "Checks the website for accessibility issues."

        results = [
            (
                issue.id,
                issue.impact.upper(),
                issue.target,
                issue.help,
                issue.screenshot,
            )
            for issue in page.accessibility
        ]

        if len(results) == 0:
            self.save_result("Perfect, no problems found by automated check.", Status.OK)
        elif any(
            issue.impact == Impact.CRITICAL.value or issue.impact == Impact.SERIOUS.value
            for issue in page.accessibility
        ):
            self.save_result(
                f"Found {len(results)} {Impact.SERIOUS.value} or {Impact.CRITICAL.value} problems by automated check.",
                Status.FAILED,
            )
        else:
            self.save_result(
                f"Warning, found {len(results)} {Impact.MINOR.value} or {Impact.MODERATE.value} problems by automated "
                "check.",
                Status.WARNING,
            )

        self.result.update({"accessibility": results})
        return self
