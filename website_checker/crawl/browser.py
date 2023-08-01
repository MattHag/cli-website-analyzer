import datetime
import time

from loguru import logger
from playwright.sync_api import Page, sync_playwright


class Browser:
    def __init__(self, headless=True, rate_limit=None):
        self.headless = headless
        self.playwright = None
        self._browser = None
        self.page = None
        self.rate_limit = rate_limit
        self._last_request = None
        if self.rate_limit:
            self._last_request = datetime.datetime.now() - datetime.timedelta(milliseconds=(rate_limit + 1000))

    def goto(self, url: str, hooks=None) -> Page:
        context = self._browser.new_context()  # incognito mode
        self.page = context.new_page()
        if hooks:
            self._register_hooks(*hooks)
        self._wait_rate_limit()
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

    def _wait_rate_limit(self):
        """Waits until given rate limit is reached."""
        if self.rate_limit:
            time_delta = datetime.datetime.now() - self._last_request
            if time_delta.total_seconds() < self.rate_limit:
                sleep_time = self.rate_limit - time_delta.total_seconds()
                logger.debug("Sleeping for %d milliseconds" % sleep_time)
                time.sleep(sleep_time / 1000)
            self._last_request = datetime.datetime.now()

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self._browser = self.playwright.chromium.launch(headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.playwright.stop()
