from website_checker.analyze import base_analyzer
from website_checker.analyze.result import Status


class CheckResourceLoadErrors(base_analyzer.BaseAnalyzer):
    def check(self, page):
        self.title = "Resource load errors"
        self.description = "Searches for resources that do not load."

        invalid_access = []
        for resource in page.failed_requests:
            if resource.failure:
                invalid_access.append(f"{resource.url}, {resource.failure}")
        for resource in page.elements:
            if resource.status_code and (400 <= resource.status_code <= 499):
                invalid_access.append(f"{resource.url}, {resource.status_code}")

        if invalid_access:
            self.save_result(invalid_access, Status.WARNING)
        else:
            self.save_result("Nice, all resources load as expected.", Status.OK)
        return self
