from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import Status


class CheckResourceSize(BaseAnalyzer):
    def check(self, page):
        self.title = "Big resources"
        self.description = "Looks for large resources that noticeably increase page load time."

        warning_limit_kb = 512
        error_limit_kb = 1024
        status = Status.OK

        external_resources = []
        for resource in page.elements:
            if getattr(resource, "headers", None) is not None:
                size_bytes = int(resource.headers.get("content-length", 0))
                if size_bytes:
                    if size_bytes > error_limit_kb * 1024:
                        status = Status.FAILED
                    if size_bytes > warning_limit_kb * 1024:
                        external_resources.append(f"{resource.url}, {int(size_bytes)/1024:.0f} kB")
                        if status.value < Status.WARNING.value:
                            status = Status.WARNING

        if external_resources:
            self.save_result(external_resources, status)
        else:
            self.save_result("Nice, no big resource found.", Status.OK)
        return self
