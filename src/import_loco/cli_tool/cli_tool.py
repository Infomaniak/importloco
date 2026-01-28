"""Command-line interface for import_loco.

This module provides the main entry point for the CLI tool and handles
command-line argument processing.
"""

import logging
import sys

from import_loco.cli_tool.arguments_parser import parse_arguments
from import_loco.core.config.config import get_project_config
from import_loco.core.exceptions import LocoError
from import_loco.core.platform_import import import_translations
from import_loco.platforms import get_platform
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

        # Load configuration
        config = get_project_config()
        logger.info("Configuration loaded successfully")
        logger.debug("Config: %s", config)

        # Get platform from config
        platform_name = config.get("platform", "ios")
        logger.info("Using platform: %s", platform_name)

        # Create platform instance
        platform = get_platform(platform_name, config)

        # Validate configuration
        platform.validate_configuration(config)

        # Determine which resources to import
        resources_to_import = []
        if arguments.check:
            # Check mode - just validate existing files
            logger.info("Running in check-only mode")
        else:
            # Import mode - determine resources based on arguments or import all
            if arguments.resource:
                resources_to_import = arguments.resource
            else:
                # Import all resource types for the platform
                resources_to_import = platform.get_resource_types()

        # Import each resource type
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