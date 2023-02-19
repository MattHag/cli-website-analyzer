import re
from typing import List, Optional

from bs4 import BeautifulSoup

from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import Status


def next_allowed_heading(heading: Optional[str] = None) -> List[str]:
    """Determines the next allowed heading level.

    Expects a heading in the format of h1, h2, h3, h4, h5 or h6 with a
    single h1 per page.
    """
    allowed_successor = []
    if heading is None:
        return ["h1"]

    current_level = int(heading[1:])
    max_next_level = current_level + 1
    max_next_level = 6 if max_next_level > 6 else max_next_level
    for level in range(2, max_next_level + 1):
        allowed_successor.append(f"h{level}")
    return allowed_successor


def shorten(text: str, length: int = 50) -> str:
    """Shortens a string to a given length and adds ellipsis."""
    return (text[:length] + "..") if len(text) > length else text


class CheckHeadingStructure(BaseAnalyzer):
    def check(self, page):
        self.title = "Heading structure"
        self.description = "Checks whether the heading structure is valid."

        soup = BeautifulSoup(page.html, "html.parser")
        page_headings = soup.find_all(re.compile("^h[1-6]$"))

        checked_headings = []
        last_heading = None
        for heading in page_headings:
            heading_level = heading.name
            checked_headings.append(f"&lt;{heading_level}&gt; {shorten(heading.text)}")

            next_expected = next_allowed_heading(last_heading)
            if heading_level not in next_expected:
                status = Status.WARNING
                self.save_result(
                    (
                        f"Heading '{shorten(heading.text)}' found as {heading_level}, "
                        f"but expected one of {', '.join(next_expected)}."
                    ),
                    status,
                )

                self.save_result(checked_headings, status)
                break
            last_heading = heading.name

        if self.result is None:
            if checked_headings:
                self.save_result("Great, the heading structure is perfect.", Status.OK)
            else:
                self.save_result("No heading found.", Status.WARNING)
        return self
