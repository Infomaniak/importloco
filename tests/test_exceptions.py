"""Tests for custom exception classes."""

import pytest

from import_loco.core.exceptions import (
    LocoError,
    LocoConfigError,
    LocoNetworkError,
    LocoParserError,
    LocoValidationError,
)


def test_loco_error_is_base_exception():
    """Test that LocoError is the base exception class."""
    error = LocoError("Test error")
    assert isinstance(error, Exception)
    assert str(error) == "Test error"


def test_loco_config_error_inherits_from_loco_error():
    """Test that LocoConfigError inherits from LocoError."""
    error = LocoConfigError("Config error")
    assert isinstance(error, LocoError)
    assert isinstance(error, Exception)
    assert str(error) == "Config error"


def test_loco_network_error_inherits_from_loco_error():
    """Test that LocoNetworkError inherits from LocoError."""
    error = LocoNetworkError("Network error")
    assert isinstance(error, LocoError)
    assert isinstance(error, Exception)
    assert str(error) == "Network error"


def test_loco_parser_error_inherits_from_loco_error():
    """Test that LocoParserError inherits from LocoError."""
    error = LocoParserError("Parser error")
    assert isinstance(error, LocoError)
    assert isinstance(error, Exception)
    assert str(error) == "Parser error"


def test_loco_validation_error_inherits_from_loco_error():
    """Test that LocoValidationError inherits from LocoError."""
    error = LocoValidationError("Validation error")
    assert isinstance(error, LocoError)
    assert isinstance(error, Exception)
    assert str(error) == "Validation error"


def test_exceptions_can_be_raised():
    """Test that all exception types can be raised and caught."""
    with pytest.raises(LocoConfigError):
        raise LocoConfigError("Config test")

    with pytest.raises(LocoNetworkError):
        raise LocoNetworkError("Network test")

    with pytest.raises(LocoParserError):
        raise LocoParserError("Parser test")

    with pytest.raises(LocoValidationError):
        raise LocoValidationError("Validation test")


def test_exceptions_can_be_caught_as_loco_error():
    """Test that specific exceptions can be caught as LocoError."""
    with pytest.raises(LocoError):
        raise LocoConfigError("Config test")

    with pytest.raises(LocoError):
        raise LocoNetworkError("Network test")

    with pytest.raises(LocoError):
        raise LocoParserError("Parser test")

    with pytest.raises(LocoError):
        raise LocoValidationError("Validation test")
