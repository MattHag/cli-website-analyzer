from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import Status


def size_humanreadable(number, suffix="B"):
    for unit in ["", "K", "M", "G"]:
        if abs(number) < 1024.0:
            return f"{number:3.1f} {unit}{suffix}"
        number /= 1024.0
    return f"{number:.1f} G{suffix}"


class CheckResourceSize(BaseAnalyzer):
    def check(self, page):
        self.title = "Total page size and big resources"
        self.description = "Finds large resources and checks total page size, which notably influence page load time."

        file_warning_limit = 512 * 1024
        file_error_limit = 1024 * 1024
        page_warning_limit = 2 * 1024 * 1024
        page_error_limit = 4 * 1024 * 1024

        assert 0 < file_warning_limit < file_error_limit
        assert 0 < page_warning_limit < page_error_limit

        big_resources = []
        page_size_bytes = 0
        page.requests.sort(key=lambda r: sum(r.sizes.values()), reverse=True)
        for resource in page.requests:
            size_bytes = int(sum([size for size in resource.sizes.values()]))
            if size_bytes > file_error_limit:
                big_resources.append(f"{resource.url}, {size_humanreadable(size_bytes)}")
                self.save_result("", Status.FAILED)
            elif size_bytes > file_warning_limit:
                big_resources.append(f"{resource.url}, {size_humanreadable(size_bytes)}")
                self.save_result("", Status.WARNING)
            page_size_bytes += size_bytes

        text_result = f"Total page size of {size_humanreadable(page_size_bytes)} is "
        if page_size_bytes <= page_warning_limit:
            text_result += "good."
            self.save_result(text_result, Status.OK)
        elif page_size_bytes >= page_error_limit:
            text_result += "big."
            self.save_result(text_result, Status.FAILED)
        else:
            text_result += "okay."
            self.save_result(text_result, Status.WARNING)

        text_result += " "
        if big_resources:
            if len(big_resources) == 1:
                text_result += "One big resource found."
            else:
                text_result += f"{len(big_resources)} big resources found."
            self.save_result(big_resources, Status.WARNING)
            self.save_result(text_result, Status.WARNING)
        else:
            text_result += "No big resources found."
            self.save_result(text_result, Status.OK)
        return self
