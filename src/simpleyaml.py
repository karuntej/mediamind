import re
from typing import TextIO, Union, Any, Dict

def _parse_value(v: str) -> Any:
    v = v.split('#',1)[0].strip()
    if v.lower() in ('true','false'):
        return v.lower() == 'true'
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v

def safe_load(stream: Union[str, TextIO]) -> Dict[str, Any]:
    """Very small YAML subset loader supporting two-level mappings."""
    if hasattr(stream, 'read'):
        text = stream.read()
    else:
        text = str(stream)
    result: Dict[str, Any] = {}
    current_key = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        if not raw.startswith(' '):
            key, _, val = raw.partition(':')
            key = key.strip()
            val = val.strip()
            if val:
                result[key] = _parse_value(val)
                current_key = None
            else:
                current_key = key
                result[current_key] = {}
        else:
            if current_key is None:
                continue
            line = raw.strip()
            k, _, v = line.partition(':')
            result[current_key][k.strip()] = _parse_value(v.strip())
    return result
