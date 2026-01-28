"""Command-line argument parsing for import_loco.

This module handles parsing of command-line arguments and options for the
import_loco CLI tool.
"""

import argparse
from argparse import Namespace


def _add_parser_arguments(parser: argparse.ArgumentParser) -> None:
    """Add command-line arguments to the parser.

    Args:
        parser: ArgumentParser instance to add arguments to.
    """
    parser.add_argument(
        "-r",
        "--resource",
        action="append",
        default=[],
        help="Specify the kind of resources to import",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="Run a complete check over the project's strings",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose mode",
    )


def parse_arguments() -> Namespace:
    """Parse command-line arguments.

    Returns:
        Namespace object containing parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="import_loco",
        description="Easily check and import the l8n strings from Loco into your projects.",
    )
    _add_parser_arguments(parser)

    parsed_arguments = parser.parse_args()

    return parsed_arguments