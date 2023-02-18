from website_checker.analyze.result import Status


class BaseAnalyzer:
    def __init__(self):
        self.title = None
        self.description = None  # Text or HTML
        self.result = None
        self.status = None

    def check(self, page):
        """Analyzes one page of a website and sets the results."""
        raise NotImplementedError

    def save_result(self, data, status: Status):
        """Sets result as ."""
        if isinstance(data, list):
            self.result = {
                "list": {"entries": data},
            }
        else:
            self.result = {"text": data}
        self.status = status.value

    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseAnalyzer:
            attrs = set(dir(C))
            if set(cls.__abstractmethods__) <= attrs:
                return True
        return NotImplemented
