import re
from datetime import datetime
from urllib.parse import urlparse


def get_domain_as_text(url):
    parsed_url = urlparse(url)
    parsed_url = re.sub(r':\d+', '', parsed_url.netloc)  # remove port
    return parsed_url.replace(".", "-")


def datetime_str(current_datetime=datetime.now()):
    return current_datetime.strftime("%Y-%m-%d %H%M")
