from bs4 import BeautifulSoup

from website_checker.analyze import base_analyzer

CMS_CLASSES = {
    "Beaver Builder": "[class^='fl-']",
    "Bricks": "[class^='brxe-']",
    "Divi": "[class^='et_pb_']",
    "Elementor": "[class^='elementor-']",
    "Jimdo": "[class^='jmd-']",
    "Oxygen Builder": "[class^='ct-']",
    "SquareSpace": "[class^='sqs-']",
    "Visual Composer": "[class^='vc_']",
}


class DetectPageBuilder(base_analyzer.BaseAnalyzer):
    def check(self, page):
        self.title = "Detect Page Builder"

        # Detect WordPress
        if any("/wp-content/" in element.url for element in page.elements):
            self.add_tags("WordPress")

        soup = BeautifulSoup(page.html, "html.parser")
        result = {}
        for cms_name, selector in CMS_CLASSES.items():
            found_classes = len(soup.select(selector))
            if found_classes:
                result[cms_name] = found_classes
        if result:
            name = max(result, key=result.get)
            self.add_tags(name)
        return self
