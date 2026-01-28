"""Platform registry and factory for translation management.

This module provides a registry of available platforms and a factory function
for creating platform instances.
"""

import logging
from typing import Any, Dict, Type

from import_loco.core.exceptions import LocoConfigError
from import_loco.platforms.base import Platform
from import_loco.platforms.ios import IOSPlatform
from import_loco.platforms.macos import MacOSPlatform

logger = logging.getLogger(__name__)

# Registry of available platforms
_PLATFORM_REGISTRY: Dict[str, Type[Platform]] = {
    "ios": IOSPlatform,
    "macos": MacOSPlatform,
}


def get_platform(platform_name: str, config: Dict[str, Any]) -> Platform:
    """Get a platform instance by name.

    Args:
        platform_name: Name of the platform (e.g., "ios", "macos", "windows", "linux").
        config: Configuration dictionary for the platform.

    Returns:
        Platform instance.

    Raises:
        LocoConfigError: If the platform is not supported.
    """
    platform_name = platform_name.lower()

    if platform_name not in _PLATFORM_REGISTRY:
        available_platforms = ", ".join(_PLATFORM_REGISTRY.keys())
        logger.error("Unsupported platform: %s", platform_name)
        raise LocoConfigError(
            f"Unsupported platform: {platform_name}. " f"Available platforms: {available_platforms}"
        )

    platform_class = _PLATFORM_REGISTRY[platform_name]
    logger.info("Creating platform instance: %s", platform_name)
    return platform_class(config)


def list_available_platforms() -> list[str]:
    """Get a list of all available platform names.

    Returns:
        List of platform names.
    """
    return list(_PLATFORM_REGISTRY.keys())


def register_platform(platform_class: Type[Platform]) -> None:
    """Register a new platform type.

    This allows for dynamic registration of custom platforms.

    Args:
        platform_class: Platform class to register.

    Raises:
        ValueError: If the platform is already registered.
    """
    # Create a temporary instance to get the name (pass empty config for registration)
    temp_instance = platform_class({})
    platform_name = temp_instance.name.lower()

    if platform_name in _PLATFORM_REGISTRY:
        raise ValueError(f"Platform already registered: {platform_name}")

    _PLATFORM_REGISTRY[platform_name] = platform_class
    logger.info("Registered new platform: %s", platform_name)
