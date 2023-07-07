from pathlib import Path

from website_checker.crawl.axe.parameters import Parameters


class Axe:
    def __init__(self):
        self.settings = Parameters()

    def configure(self, params: Parameters):
        self.settings = params

    def run_check(self, page):
        page.wait_for_load_state("domcontentloaded")
        axe_file = Path() / "crawl" / "axe" / "resources" / "axe.js"
        js_text = axe_file.read_text()
        page.evaluate("async (js)=> await window.eval(js)", js_text)
        data = page.evaluate(
            "async (param) => await axeData(param)", self.settings.to_json()
        )
        return data
