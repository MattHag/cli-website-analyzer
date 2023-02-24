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

        requests = len(page.requests)
        text_result = f" {requests} requests are made, "
        if requests <= 80:
            text_result += "that is good."
            self.save_result(text_result, Status.OK)
        elif requests >= 120:
            text_result += "these are many."
            self.save_result(text_result, Status.FAILED)
        else:
            text_result += "which is okay."
            self.save_result(text_result, Status.WARNING)

        text_result += " "
        if invalid_access:
            self.save_result(invalid_access, Status.WARNING)
            if len(invalid_access) == 1:
                text_result += "One resource failed to load:"
            else:
                text_result += f"{len(invalid_access)} resources failed to load:"
        else:
            text_result += "All resources load as expected."
        self.save_result(text_result, Status.OK)
        return self
