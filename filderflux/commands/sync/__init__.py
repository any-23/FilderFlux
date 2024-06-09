import argparse
from filderflux.commands.sync.sync import handle_sync


def add_sync_parser(subparsers: argparse._SubParsersAction) -> None:
    parser_sync = subparsers.add_parser("sync", help="Synchronisation of the source folder and the replica.")
    parser_sync.add_argument("-s", "--source", type=str, required=True, help="Determination of the source folder.")
    parser_sync.add_argument("-r", "--replica", type=str, required=True, help="Determination of the replica folder.")
    parser_sync.add_argument(
        "-i", "--interval", type=float, default=1, help="The interval between runs held in seconds."
    )
    parser_sync.set_defaults(func=handle_sync)
