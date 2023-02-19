from collections import Counter

from bs4 import BeautifulSoup

from website_checker.analyze import base_analyzer
from website_checker.analyze.result import Status

STRUCTURAL_SEMANTIC_TAGS = ["header", "nav", "main", "section", "article", "aside", "footer"]


class CheckSemanticHtml(base_analyzer.BaseAnalyzer):
    def check(self, page):
        self.title = "Semantic HTML tags"
        self.description = "Checks usage of structural semantic HTML tags, which are good for accessibility and SEO."

        soup = BeautifulSoup(page.html, "html.parser")
        found_tags = [element.name for element in soup.find_all(STRUCTURAL_SEMANTIC_TAGS)]

        c = Counter(found_tags)
        tags_with_count = ", ".join([f"{tag} ({count})" for tag, count in c.items()])

        if found_tags:
            self.save_result(
                f"Good, {len(found_tags)} structural semantic tags are used: {tags_with_count}",
                Status.OK,
            )
        else:
            self.save_result("No structural semantic tags found. Consider adding some.", Status.WARNING)
        return self
