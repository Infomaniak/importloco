import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import urlretrieve

import requests

from import_loco.core.exceptions import LocoNetworkError

logger = logging.getLogger(__name__)

BASE_URL = "https://localise.biz/api"


def fetch_archive(path: str, filters: str, loco_key: str) -> str:
    query_params = _get_default_query_params(filters, loco_key)
    endpoint = _create_endpoint(f"/export/archive/{path}", query_params)

    logger.debug("Downloading archive from %s", path)
    archive_path = _download_archive(endpoint)
    logger.debug("Archive downloaded successfully to %s", archive_path)
    return archive_path


def fetch_tags(loco_key: str) -> Optional[List[str]]:
    endpoint = _create_endpoint("/tags")

    headers = {"Authorization": f"Loco {loco_key}"}
    logger.debug("Fetching tags from Loco API")

    try:
        response = requests.get(endpoint, headers=headers, timeout=30)
        response.raise_for_status()

        tags = response.json()
        logger.debug("Successfully fetched %d tags", len(tags))
        return tags
    except requests.RequestException as e:
        raise LocoNetworkError(f"Failed to fetch tags from Loco API: {e}")


# -- Utils


def _create_endpoint(path: str, query_params: Optional[Dict[str, Any]] = None) -> str:
    url = f"{BASE_URL}{path}"
    if query_params is not None:
        encoded_query_params = urlencode(query_params)
        url += "?%s" % encoded_query_params

    return url


def _get_default_query_params(filters: str, loco_key: str) -> Dict[str, Any]:
    query_params = {"fallback": "en", "order": "id", "charset": "utf8", "filter": filters, "key": loco_key}
    return {key: value for key, value in query_params.items() if value is not None}


def _download_archive(endpoint: str) -> str:
    try:
        local_filename, _ = urlretrieve(endpoint)
        return local_filename
    except Exception as e:
        raise LocoNetworkError(f"Failed to download archive from {endpoint}: {e}")
