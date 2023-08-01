import re

from bs4 import BeautifulSoup

from website_checker.analyze import base_analyzer

DETECTED_CLASSES = {
    "Beaver Builder": "[class^='fl-']",
    "Bricks": "[class^='brxe-']",
    "Divi": "[class^='et_pb_']",
    "Elementor": "[class^='elementor-']",
    "Jimdo": "[class^='jmd-']",
    "Oxygen Builder": "[class^='ct-']",
    "SquareSpace": "[class^='sqs-']",
    "Visual Composer": "[class^='vc_']",
}


class DetectCMSPageBuilder(base_analyzer.BaseAnalyzer):
    def __init__(self):
        super().__init__(hidden=True)

    def check(self, page):
        self.title = "Detect CMS and Page Builder"
        soup = BeautifulSoup(page.html, "html.parser")

        if any(
            re.search(r"WordPress \d+", element.get("content"))
            for element in soup.find_all("meta", attrs={"name": re.compile(r"generator", re.I)})
        ):
            self.add_tags("WordPress")
        elif any("/wp-content/" in element.url for element in page.elements):
            self.add_tags("WordPress")
        elif any(
            "TYPO3 CMS" == element.get("content")
            for element in soup.find_all("meta", attrs={"name": re.compile(r"generator", re.I)})
        ):
            self.add_tags("TYPO3")
        elif any("/typo3" in element.url for element in page.elements):
            self.add_tags("TYPO3")
        elif any(
            re.search(r"Drupal \d+ \(https://www.drupal.org\)", element.get("content"))
            for element in soup.find_all("meta", attrs={"name": re.compile(r"generator", re.I)})
        ):
            self.add_tags("Drupal")
        elif any("/sites/default/files/" in element.url for element in page.elements):
            self.add_tags("Drupal")
        elif any("/shopifycloud/shopify/assets/" in element.url for element in page.elements):
            self.add_tags("Shopify")
        elif any(
            "Joomla! - Open Source Content Management" == element.get("content")
            for element in soup.find_all("meta", attrs={"name": re.compile(r"generator", re.I)})
        ):
            self.add_tags("Joomla")

        result = {}
        for builder_name, selector in DETECTED_CLASSES.items():
            found_classes = len(soup.select(selector))
            if found_classes:
                result[builder_name] = found_classes
        if result:
            selected_name = max(result, key=result.get)
            self.add_tags(selected_name)
        return self
