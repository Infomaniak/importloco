"""Network operations for communicating with the Loco API.

This module handles all HTTP requests to the Loco API, including fetching
translation archives and retrieving project metadata.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import urlretrieve

import requests

from import_loco.core.exceptions import LocoNetworkError

logger = logging.getLogger(__name__)

BASE_URL = "https://localise.biz/api"


def fetch_archive(path: str, filters: str, loco_key: str) -> str:
    """Download a translation archive from Loco.

    Args:
        path: API endpoint path for the archive type (e.g., "strings.zip").
        filters: Comma-separated list of filters to apply.
        loco_key: Loco API authentication key.

    Returns:
        Path to the downloaded archive file.

    Raises:
        LocoNetworkError: If the download fails.
    """
    query_params = _get_default_query_params(filters, loco_key)
    endpoint = _create_endpoint(f"/export/archive/{path}", query_params)

    logger.info("Downloading archive from %s", path)
    archive_path = _download_archive(endpoint)
    logger.info("Archive downloaded successfully to %s", archive_path)
    return archive_path


def fetch_tags(loco_key: str) -> Optional[List[str]]:
    """Fetch all tags from the Loco project.

    Args:
        loco_key: Loco API authentication key.

    Returns:
        List of tag names, or None if the request fails.

    Raises:
        LocoNetworkError: If the API request fails.
    """
    endpoint = _create_endpoint("/tags")

    headers = {"Authorization": f"Loco {loco_key}"}
    logger.info("Fetching tags from Loco API")

    try:
        response = requests.get(endpoint, headers=headers, timeout=30)
        response.raise_for_status()

        if response.status_code == 200:
            tags = response.json()
            logger.info("Successfully fetched %d tags", len(tags))
            return tags
        else:
            logger.warning("Unexpected status code %d when fetching tags", response.status_code)
            return None
    except requests.RequestException as e:
        logger.error("Failed to fetch tags: %s", e)
        raise LocoNetworkError(f"Failed to fetch tags from Loco API: {e}")


# -- Utils


def _create_endpoint(path: str, query_params: Optional[Dict[str, Any]] = None) -> str:
    """Construct a full API endpoint URL.

    Args:
        path: API path (e.g., "/tags").
        query_params: Optional dictionary of query parameters.

    Returns:
        Complete URL with encoded query parameters if provided.
    """
    url = f"{BASE_URL}{path}"
    if query_params is not None:
        encoded_query_params = urlencode(query_params)
        url += "?%s" % encoded_query_params

    return url


def _get_default_query_params(filters: str, loco_key: str) -> Dict[str, Any]:
    """Generate default query parameters for archive downloads.

    Args:
        filters: Comma-separated list of filters.
        loco_key: Loco API authentication key.

    Returns:
        Dictionary of query parameters with None values filtered out.
    """
    query_params = {"fallback": "en", "order": "id", "charset": "utf8", "filter": filters, "key": loco_key}
    return {key: value for key, value in query_params.items() if value is not None}


def _download_archive(endpoint: str) -> str:
    """Download a file from the given endpoint.

    Args:
        endpoint: Full URL to download from.

    Returns:
        Path to the downloaded file.

    Raises:
        LocoNetworkError: If the download fails.
    """
    try:
        local_filename, _ = urlretrieve(endpoint)
        return local_filename
    except Exception as e:
        logger.error("Failed to download archive: %s", e)
        raise LocoNetworkError(f"Failed to download archive from {endpoint}: {e}")
