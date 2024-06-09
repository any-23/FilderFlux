import argparse
import logging

logger = logging.getLogger(__name__)


def handle_sync(args: argparse.Namespace) -> None:
    logger.info(
        f"Source folder is {args.source}.  Replica folder is {args.replica}. Interval is set to {args.interval} seconds."
    )
