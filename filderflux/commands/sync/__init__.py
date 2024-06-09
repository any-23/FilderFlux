import argparse
from filderflux.commands.sync.sync import handle_sync


def add_sync_parser(subparsers: argparse._SubParsersAction) -> None:
    parser_sync = subparsers.add_parser("sync", help="Print version of FilderFlux")
    parser_sync.add_argument("-s", "--source", type=str, required=True)
    parser_sync.add_argument("-r", "--replica", type=str, required=True)
    parser_sync.add_argument("-i", "--interval", type=float, default=1)
    parser_sync.set_defaults(func=handle_sync)
