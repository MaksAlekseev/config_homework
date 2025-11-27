import subprocess
import sys
from pathlib import Path

import toml


def run_cli(input_text: str, tmp_path: Path):
    out_file = tmp_path / "out.toml"
    cmd = [sys.executable, "-m", "ucfg2toml.cli", "-o", str(out_file)]
    proc = subprocess.run(
        cmd,
        input=input_text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc, out_file


def test_cli_success(tmp_path):
    src = "@{ key = 0o7; }"
    proc, out_file = run_cli(src, tmp_path)
    assert proc.returncode == 0
    assert out_file.exists()
    data = toml.load(out_file)
    assert data["key"] == 7


def test_cli_error_on_syntax(tmp_path):
    src = "@{ key 0o7; }"  # синтаксическая ошибка
    proc, out_file = run_cli(src, tmp_path)
    assert proc.returncode != 0
    # При ошибке файл не должен быть создан.
    assert not out_file.exists()
