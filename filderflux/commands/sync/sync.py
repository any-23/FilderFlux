import argparse
import logging

logger = logging.getLogger(__name__)


def handle_sync(args: argparse.Namespace) -> None:
    logger.info(f"Source is {args.source}.  Replica is {args.replica}. Interval is {args.interval}.")
