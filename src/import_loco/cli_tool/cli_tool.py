"""Command-line interface for import_loco.

This module provides the main entry point for the CLI tool and handles
command-line argument processing.
"""

import logging
import sys

from import_loco.cli_tool.arguments_parser import parse_arguments
from import_loco.core.config.config import get_project_config
from import_loco.core.exceptions import LocoError
import import_loco.helpers.utils as utils

logger = logging.getLogger(__name__)


def run_tool() -> None:
    """Run the import_loco CLI tool.

    This is the main entry point that processes arguments, loads configuration,
    and executes the import workflow.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        arguments = parse_arguments()

        if arguments.verbose:
            utils.is_verbose = True
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Verbose mode enabled")

        config = get_project_config()
        logger.info("Configuration loaded successfully")
        logger.debug("Config: %s", config)

        # TODO: Import, parse and move files
        # This will be implemented in Phase 2

        sys.exit(0)
    except LocoError as e:
        logger.error("Import failed: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Import cancelled by user")
        print("\nImport cancelled.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)