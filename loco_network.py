from urllib.request import urlretrieve
from urllib.parse import urlencode

BASE_URL = "https://localise.biz/api/export/archive"

def fetch_strings(filters, loco_key):
    return _fetch_archive("/strings.zip", filters, loco_key)


def fetch_stringsdict(filters, loco_key):
    return _fetch_archive("/stringsdict.zip", filters, loco_key)

# -- Utils

def _create_endpoint(path, query_params = None):
    url = f"{BASE_URL}{path}"
    if query_params is not None:
        encoded_query_params = urlencode(query_params)
        url += f"?%s" % encoded_query_params

    return  url


def _get_default_query_params(filters, loco_key):
    query_params = {
        "fallback": "en",
        "order": "id",
        "charset": "utf8",
        "filter": filters,
        "key": loco_key
    }
    return { key: value for key, value in query_params.items() if value is not None }


def _download_archive(endpoint):
    local_filename, _ = urlretrieve(endpoint)
    return local_filename


def _fetch_archive(path, filters, loco_key):
    query_params = _get_default_query_params(filters, loco_key)
    endpoint = _create_endpoint(path, query_params)

    return _download_archive(endpoint)
