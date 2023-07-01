from datetime import datetime

from website_checker import utils


def test_get_domain_as_text():
    url = "https://www.domain.test/subdirectory/test"
    expected_domain = "www-domain-test"

    domain = utils.get_domain_as_text(url)

    assert domain == expected_domain


def test_datetime_str():
    expected_datetime_str = "2021-01-01 0000"
    datetime_str = utils.datetime_str(datetime(2021, 1, 1))

    assert datetime_str == expected_datetime_str
