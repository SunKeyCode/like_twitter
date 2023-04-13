from typing import Any, List


def reformat_any_response(
    value: Any | List[Any], key: str | List[str] | None = None
) -> dict[str, Any]:
    if isinstance(key, list) and isinstance(value, list) and len(key) == len(value):
        key.append("result")
        value.append(True)
        return dict(zip(key, value))
    elif isinstance(key, str):
        return {"result": True, key: value}
    else:
        raise TypeError


def reformat_error(exc: tuple) -> str:
    try:
        return exc[0][0]
    except IndexError:
        return "error massage failed"
