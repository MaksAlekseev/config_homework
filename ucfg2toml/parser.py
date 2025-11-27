from __future__ import annotations

from typing import Any

from lark import Lark, Transformer, UnexpectedInput


class ConfigSyntaxError(Exception):
    """Синтаксическая ошибка входного конфигурационного файла."""


class ConfigSemanticError(Exception):
    """Семантическая ошибка (неизвестная константа, дублирующий ключ и т.п.)."""


GRAMMAR = r"""
start: const_decl* value

const_decl: "var" NAME value

?value: number
      | string
      | dict
      | const_ref

number: OCT_NUMBER
string: STRING
dict: "@{" pair* "}"
pair: NAME "=" value ";"

const_ref: CONST_REF

OCT_NUMBER: "0" ("o"|"O") /[0-7]+/
STRING: /\[\[(.|\n)*?]]/
CONST_REF: /\$[a-z][a-z0-9_]*\$/
NAME: /[a-z][a-z0-9_]*/

%import common.WS
%ignore WS
"""

_parser = Lark(GRAMMAR, start="start", parser="lalr", propagate_positions=True)


class EvalTransformer(Transformer):
    """
    Трансформер, который сразу:
    - вычисляет значения констант,
    - превращает синтаксическое дерево в обычные Python-объекты.
    """

    def __init__(self):
        super().__init__()
        self.constants: dict[str, Any] = {}

    def number(self, items):
        # Формат: 0oXYZ (или 0OXYZ) — это восьмеричное число.
        text = str(items[0])
        # отбрасываем "0o" / "0O"
        return int(text[2:], 8)

    def string(self, items):
        # Формат: [[...]]
        text = str(items[0])
        return text[2:-2]

    def pair(self, items):
        name_token, value = items
        name = str(name_token)
        return name, value

    def dict(self, items):
        result: dict[str, Any] = {}
        for name, value in items:
            if name in result:
                raise ConfigSemanticError(f"Duplicate key '{name}' in dictionary")
            result[name] = value
        return result

    def const_ref(self, items):
        # Формат: $имя$
        token = items[0]
        text = str(token)
        name = text[1:-1]
        if name not in self.constants:
            raise ConfigSemanticError(f"Unknown constant '{name}'")
        return self.constants[name]

    def const_decl(self, items):
        name_token, value = items
        name = str(name_token)
        if name in self.constants:
            raise ConfigSemanticError(f"Constant '{name}' already defined")
        self.constants[name] = value
        # Объявление константы не попадает в итоговое значение.
        return None

    def start(self, items):
        # Среди дочерних элементов start будут:
        # - None для объявлений констант,
        # - одно итоговое value.
        values = [item for item in items if item is not None]
        if len(values) != 1:
            raise ConfigSemanticError(
                "Configuration must contain exactly one top-level value"
            )
        return values[0]


def parse_source(source: str) -> Any:
    """
    Парсит исходный текст конфигурации и возвращает Python-значение:
    - dict для @{ ... },
    - int для чисел,
    - str для строк.

    При ошибке синтаксиса/семантики выбрасывает ConfigSyntaxError/ConfigSemanticError.
    """
    try:
        tree = _parser.parse(source)
    except UnexpectedInput as e:
        # Красивое сообщение об ошибке с номером строки и столбца.
        context = e.get_context(source)
        msg = f"Syntax error at line {e.line}, column {e.column}:\n{context}"
        raise ConfigSyntaxError(msg) from e
    except Exception as e:
        raise ConfigSyntaxError(str(e)) from e

    transformer = EvalTransformer()
    try:
        return transformer.transform(tree)
    except ConfigSemanticError:
        raise
    except Exception as e:
        raise ConfigSemanticError(str(e)) from e
