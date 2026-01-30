import logging
from import_loco.helpers.global_variables import is_verbose

logger = logging.getLogger(__name__)


def print_if_verbose(value: str) -> None:
    if not is_verbose:
        return
    print(value)
