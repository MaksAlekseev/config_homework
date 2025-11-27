import pytest

from ucfg2toml.parser import parse_source, ConfigSemanticError, ConfigSyntaxError


def test_parse_number_octal():
    # 0o10 в восьмеричной системе — это 8 в десятичной.
    result = parse_source("0o10")
    assert result == 8


def test_parse_string():
    result = parse_source("[[hello]]")
    assert result == "hello"


def test_parse_simple_dict():
    src = "@{ key = 0o7; }"
    result = parse_source(src)
    assert isinstance(result, dict)
    assert result["key"] == 7


def test_nested_dict():
    src = "@{ outer = @{ inner = 0o1; }; }"
    result = parse_source(src)
    assert result["outer"]["inner"] == 1


def test_constants_basic():
    src = """\
var x 0o10
@{ value = $x$; }
"""
    result = parse_source(src)
    assert result["value"] == 8


def test_unknown_constant_raises():
    src = "@{ value = $x$; }"
    with pytest.raises(ConfigSemanticError):
        parse_source(src)


def test_duplicate_key_in_dict():
    src = "@{ key = 0o1; key = 0o2; }"
    with pytest.raises(ConfigSemanticError):
        parse_source(src)


def test_syntax_error_missing_equal():
    src = "@{ key 0o1; }"  # отсутствует знак '='
    with pytest.raises(ConfigSyntaxError):
        parse_source(src)
