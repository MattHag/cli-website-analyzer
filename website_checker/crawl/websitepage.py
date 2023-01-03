from datetime import datetime

from website_checker.crawl.cookie import Cookie


class WebsitePage:
    def __init__(self, url="", title="", html="", cookies=None, elements=None):
        if elements is None:
            elements = []
        if cookies is None:
            cookies = []
        self.url = url
        self.title = title
        self.html = html
        self.cookies = cookies
        self.elements = elements
        self.created = datetime.now()

    def add_cookie(self, cookie: Cookie):
        self.cookies.append(cookie)

    def add_element(self, element):
        self.elements.append(element)
