"""Command-line interface for import_loco.

This module provides the main entry point for the CLI tool and handles
command-line argument processing.
"""

import logging
import sys

from import_loco.cli_tool import arguments_parser
from import_loco.core.config.config import get_project_config
from import_loco.core.exceptions import LocoError
from import_loco.core.platform_import import import_translations
from import_loco.platforms import get_platform
import import_loco.helpers.utils as utils

logger = logging.getLogger(__name__)


def run_tool() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        arguments = arguments_parser.parse_arguments()

        if arguments.verbose:
            utils.is_verbose = True
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Verbose mode enabled")

        config = get_project_config()
        logger.info("Configuration loaded successfully")
        logger.debug("Config: %s", config)

        platform_name = config.get("platform", "ios")
        logger.info("Using platform: %s", platform_name)

        platform = get_platform(platform_name, config)

        platform.validate_configuration(config)

        resources_to_import = []
        if arguments.check:
            logger.info("Running in check-only mode")
        else:
            if arguments.resource:
                resources_to_import = arguments.resource
            else:
                resources_to_import = platform.get_resource_types()

        all_success = True
        for resource_type in resources_to_import:
            logger.info("Importing resource type: %s", resource_type)
            try:
                success = import_translations(platform, resource_type)
                if not success:
                    all_success = False
                    logger.warning("Import completed with validation errors for: %s", resource_type)
            except Exception as e:
                logger.error("Failed to import %s: %s", resource_type, e)
                all_success = False

        if all_success:
            logger.info("Import completed successfully")
            sys.exit(0)
        else:
            logger.warning("Import completed with errors")
            sys.exit(1)

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
