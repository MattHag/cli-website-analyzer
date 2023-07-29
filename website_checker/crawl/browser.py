from playwright.sync_api import Page, sync_playwright


class Browser:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self._browser = None
        self.page = None

    def goto(self, url: str, hooks=None) -> Page:
        context = self._browser.new_context()  # incognito mode
        self.page = context.new_page()
        if hooks:
            self._register_hooks(*hooks)
        self.page.goto(url, wait_until="networkidle")
        return self.page

    def close_page(self):
        if self.page:
            self.page.close()

    def _register_hooks(self, request_failed, response, request_finished, download):
        self.page.on("requestfailed", request_failed)
        self.page.on("response", response)
        self.page.on("requestfinished", request_finished)
        self.page.on("download", download)

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self._browser = self.playwright.chromium.launch(headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.playwright.stop()
