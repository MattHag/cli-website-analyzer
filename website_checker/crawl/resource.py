class Resource:
    def __init__(self, url, status_code=None, headers=None):
        self.url = url
        self.status_code = status_code
        self.headers = headers  # content-length, content-type
