import argparse
from filderflux.commands.version import add_version_parser
from filderflux.commands.sync import add_sync_parser
import logging
import sys


def configure_logger(args: argparse.Namespace):
    # Configures the root_logger with a console handler to output log messages to stdout.
    # Adds a file handler to log messages to the specified file.

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(args.log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def process_parser():
    parser = argparse.ArgumentParser(description="Simple tool for folder synchronisation")
    parser.add_argument("-l", "--log-file", type=str, required=True, help="Path to the logfile")
    subparsers = parser.add_subparsers(help="Available commands")

    # your commands go here
    add_version_parser(subparsers)
    add_sync_parser(subparsers)

    args = parser.parse_args()
    configure_logger(args)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def main():  # entry point of filderflux
    process_parser()
