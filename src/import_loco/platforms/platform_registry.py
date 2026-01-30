import logging
from typing import Any, Dict, Type

from import_loco.core.exceptions import LocoConfigError
from import_loco.platforms.base import Platform
from import_loco.platforms.ios import IOSPlatform
from import_loco.platforms.macos import MacOSPlatform
from import_loco.platforms.windows import WindowsPlatform

logger = logging.getLogger(__name__)

_PLATFORM_REGISTRY: Dict[str, Type[Platform]] = {
    "ios": IOSPlatform,
    "macos": MacOSPlatform,
    "windows": WindowsPlatform,
}


def get_platform(platform_name: str, config: Dict[str, Any]) -> Platform:
    platform_name = platform_name.lower()

    if platform_name not in _PLATFORM_REGISTRY:
        available_platforms = ", ".join(_PLATFORM_REGISTRY.keys())
        raise LocoConfigError(f"Unsupported platform: {platform_name}. Available platforms: {available_platforms}")

    platform_class = _PLATFORM_REGISTRY[platform_name]
    logger.debug("Creating platform instance: %s", platform_name)
    return platform_class(config)
