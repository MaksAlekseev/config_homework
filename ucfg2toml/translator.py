from __future__ import annotations

from typing import Any, Dict

from .parser import parse_source, ConfigSyntaxError, ConfigSemanticError


def translate_to_python(source: str) -> Dict[str, Any]:
    """
    Переводит текст учебного конфигурационного языка
    в Python-словарь, готовый к сериализации в TOML.

    Требование: верхнеуровневое значение должно быть словарём @{ ... }.
    """
    value = parse_source(source)
    if not isinstance(value, dict):
        raise ConfigSemanticError("Top-level value must be a dictionary (@{ ... })")
    return value


__all__ = ["translate_to_python", "ConfigSyntaxError", "ConfigSemanticError"]
