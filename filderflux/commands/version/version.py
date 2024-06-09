import argparse
from importlib.metadata import PackageNotFoundError, version
import logging

logger = logging.getLogger(__name__)


def cli_version() -> str:
    try:
        return version("filderflux")
    except PackageNotFoundError:
        return ""


def handle_version(args: argparse.Namespace) -> None:
    version = cli_version()
    if version:
        logger.info(f"Version of filderflux is {version}.")
    else:
        logger.warning("Package is not installed.")
