# Testing functionality:
# - sample testing file
# - mocking external version function from importlib to avoid test dependency on git tag
# - mocking in-house cli_version function to test handle_version

from unittest.mock import patch
from importlib.metadata import PackageNotFoundError
from filderflux.commands.version.version import cli_version

# artificial version for mocking
MOCK_VERSION = "0.0.5"


def test_cli_version_installed():
    with patch("filderflux.commands.version.version.version", return_value=MOCK_VERSION):
        assert cli_version() == MOCK_VERSION


def test_cli_version_not_installed():
    with patch("filderflux.commands.version.version.version", side_effect=PackageNotFoundError):
        assert cli_version() == ""
