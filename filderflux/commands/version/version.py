import argparse
from importlib.metadata import PackageNotFoundError, version


def cli_version() -> str:
    try:
        return version("filderflux")
    except PackageNotFoundError:
        return ""


def handle_version(args: argparse.Namespace) -> None:
    version = cli_version()
    if version:
        print(f"Version of filderflux is {version}.")
    else:
        print("Package is not installed.")
