from unittest.mock import patch

import pytest

from website_checker import utils


@pytest.fixture
def mock_desktop_path(tmp_path):
    with patch.object(utils, "get_desktop_path") as mock_get_desktop_path:
        mock_get_desktop_path.return_value = tmp_path
        yield mock_get_desktop_path
