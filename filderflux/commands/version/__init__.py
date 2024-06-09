import argparse
from filderflux.commands.version.version import handle_version


def add_version_parser(subparsers: argparse._SubParsersAction) -> None:
    parser_version = subparsers.add_parser("version", help="Print version of FilderFlux")
    parser_version.set_defaults(func=handle_version)
