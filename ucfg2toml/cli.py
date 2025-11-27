from __future__ import annotations

import argparse
import sys
from pathlib import Path

import toml

from .translator import translate_to_python, ConfigSyntaxError, ConfigSemanticError


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Учебный транслятор конфигурационного языка в TOML."
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Путь к выходному TOML-файлу.",
    )
    args = parser.parse_args(argv)

    # Читаем весь вход целиком из stdin.
    source = sys.stdin.read()

    try:
        data = translate_to_python(source)
    except ConfigSyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        return 1
    except ConfigSemanticError as e:
        print(f"Semantic error: {e}", file=sys.stderr)
        return 1

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        toml.dump(data, f)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
