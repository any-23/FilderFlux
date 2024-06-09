import argparse
from filderflux.commands.version import add_version_parser


def process_parser():
    parser = argparse.ArgumentParser(description="Simple tool for folder synchronisation")
    subparsers = parser.add_subparsers(help="Available commands")

    # your commands go here
    add_version_parser(subparsers)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def main():  # entry point of filderflux
    process_parser()
