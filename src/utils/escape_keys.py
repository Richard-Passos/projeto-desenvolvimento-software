import re
from typing import Any


def escape_keys(map: dict[str, Any]) -> str:
    keys = [re.escape(key) for key in map]
    return '|'.join(keys)
