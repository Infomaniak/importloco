"""Command-line interface for import_loco.

This module provides the main entry point for the CLI tool and handles
command-line argument processing.
"""

import logging
import sys

from import_loco.cli_tool import arguments_parser
from import_loco.core.config.config import get_project_config
from import_loco.core.exceptions import LocoError
from import_loco.core.loco.platform_import import import_translations
from import_loco.core.platforms.platform_registry import get_platform

logger = logging.getLogger(__name__)


def run_tool() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
    )

    try:
        arguments = arguments_parser.parse_arguments()

        if arguments.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Verbose mode enabled")

        config = get_project_config()
        logger.debug("Configuration loaded successfully")
        logger.debug("Config: %s", config)

        platform_name = config.get("platform", "ios")
        platform = get_platform(platform_name, config)
        platform.validate_configuration(config)

        resources_to_import = []
        if arguments.check:
            print("Running in check-only mode")
        else:
            if arguments.resource:
                resources_to_import = arguments.resource
            else:
                resources_to_import = platform.get_resource_types()

        for resource_type in resources_to_import:
            import_translations(platform, resource_type)

        # TODO: Check strings

    except LocoError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
