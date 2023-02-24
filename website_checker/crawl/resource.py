class ResourceRequest:
    def __init__(self, url, sizes=None, failure=None, headers=None):
        self.url = url
        self.sizes = sizes
        self.failure = failure
        self.headers = headers


class Resource:
    def __init__(self, url, status_code=None, headers=None):
        self.url = url
        self.status_code = status_code
        self.headers = headers  # content-length, content-type
