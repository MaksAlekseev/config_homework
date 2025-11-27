import pytest

from ucfg2toml.translator import translate_to_python, ConfigSemanticError


def test_top_level_must_be_dict():
    # Число на верхнем уровне — это ошибка.
    with pytest.raises(ConfigSemanticError):
        translate_to_python("0o10")


def test_translate_nested_dict():
    src = "@{ a = 0o1; b = @{ c = 0o2; }; }"
    result = translate_to_python(src)
    assert result == {"a": 1, "b": {"c": 2}}
