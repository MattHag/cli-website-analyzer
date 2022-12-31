class PageResult:
    def __init__(self, url: str, title: str, results: list = []):
        self.url = url
        self.title = title
        self.results = results

    def add_evaluation(self, evaluation):
        self.results.append(evaluation)


class AnalyzerResult:
    def __init__(self, title: str, description=None):
        self.title = title
        self.description = description
        self.result = None

    def set_result(self, result):
        """Sets result as text paragraph."""
        self.result = result

    def add_element(self, element):
        """Sets result as list of entries."""
        if self.result is None:
            self.result = []
        self.result.append(element)

    def as_dict(self):
        res = {
            "title": self.title,
        }
        if self.description:
            res["description"] = self.description
        if type(self.result) == list:
            res["results"] = self.result
        else:
            res["result"] = self.result
        return res

    @classmethod
    def __subclasshook__(cls, C):
        if cls is AnalyzerResult:
            attrs = set(dir(C))
            if set(cls.__abstractmethods__) <= attrs:
                return True
        return NotImplemented
