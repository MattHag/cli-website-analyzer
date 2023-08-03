import mimetypes
from typing import Dict, Tuple

from loguru import logger

from website_checker.analyze.base_analyzer import BaseAnalyzer
from website_checker.analyze.result import Status

CONTENT_TYPES_CATEGORIZED = {
    "HTML": ["text/html"],
    "Media": ["image", "video", "audio"],
    "Fonts": ["font"],
    "CSS": ["text/css"],
    "JS": ["javascript"],
    "Other": [],
}


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
        successful_requests = page.requests
        successful_requests.sort(key=lambda r: get_object_size(r), reverse=True)
        for resource in successful_requests:
            size_bytes = get_object_size(resource)
            if size_bytes > file_error_limit:
                big_resources.append(f"{resource.url}, {size_humanreadable(size_bytes)}")
                self.save_result("", Status.FAILED)
            elif size_bytes > file_warning_limit:
                big_resources.append(f"{resource.url}, {size_humanreadable(size_bytes)}")
                self.save_result("", Status.WARNING)
            page_size_bytes += size_bytes

        res_per_category = []
        for category, (count, size) in resource_size_per_category(page).items():
            if count == 0:
                continue
            res_per_category.append([category, count, f"{size_humanreadable(size)}"])
        table = {
            "heading": ["Type", "Requests", "Size"],
            "entries": res_per_category,
        }

        text_result = f"Total page size of {size_humanreadable(page_size_bytes)} is "
        if page_size_bytes <= page_warning_limit:
            text_result += "good."
            self.save_result(text_result, Status.OK)
        elif page_size_bytes >= page_error_limit:
            text_result += "big."
            self.save_result(text_result, Status.FAILED)
            if res_per_category:
                self.save_result(table, Status.OK)
        else:
            text_result += "okay."
            self.save_result(text_result, Status.WARNING)
            if res_per_category:
                self.save_result(table, Status.OK)

        text_result += " "
        if big_resources:
            if len(big_resources) == 1:
                text_result += "One big resource found."
            else:
                text_result += f"{len(big_resources)} big resources found."
            self.save_result(big_resources, Status.WARNING)
            self.save_result(text_result, Status.WARNING)
            if res_per_category:
                self.save_result(table, Status.OK)
        else:
            text_result += "No big resources found."
            self.save_result(text_result, Status.OK)

        return self


def resource_size_per_category(page) -> Dict[str, Tuple[int, int]]:
    categorized_objects = categorize_objects(page.elements)
    sorted_categories = sorted(categorized_objects.items(), key=lambda x: calculate_total_size(x[1]), reverse=True)
    result_per_category = {}
    for category, objects in sorted_categories:
        total_size = calculate_total_size(objects)
        result_per_category[category] = (len(objects), total_size)
    return result_per_category


def categorize_objects(elements):
    categorized_objects = {category: [] for category in CONTENT_TYPES_CATEGORIZED.keys()}

    for obj in elements:
        content_type = get_content_type(obj)
        for category, known_content_types in CONTENT_TYPES_CATEGORIZED.items():
            # check that any of the content_types are a substring of content_type
            if any(known_type in content_type for known_type in known_content_types):
                categorized_objects[category].append(obj)
                break
        else:
            categorized_objects['Other'].append(obj)

    return categorized_objects


def calculate_total_size(objects):
    return sum(get_object_size(obj) for obj in objects)


def get_object_size(obj):
    try:
        return int(sum(obj.request.sizes.values()))
    except AttributeError:
        pass
    try:
        return int(sum(obj.sizes.values()))
    except AttributeError:
        pass
    return 0


def get_content_type(obj):
    try:
        content_type = obj.headers["content-type"]
        return content_type
    except (KeyError, AttributeError, TypeError):
        pass
    clean_url = obj.url.split("?")[0]
    content_type = mimetypes.guess_type(clean_url)[0]
    if content_type:
        return content_type
    return "unknown"
