"""Tests for configuration loading."""

import os
import tempfile

import pytest
import yaml

from import_loco.core.config.config import (
    ProjectConfiguration,
    get_project_config,
    _read_config,
    _ensure_config_file_exist,
)
from import_loco.core.exceptions import LocoConfigError


def test_project_configuration_initialization():
    """Test ProjectConfiguration initialization."""
    config = ProjectConfiguration(
        localizable_path="/path/to/localizable",
        main_target_localizable_path="/path/to/main",
        loco_api_key="test-key-123",
        filters=["ios", "common"],
    )

    assert config.localizable_path == "/path/to/localizable"
    assert config.main_target_localizable_path == "/path/to/main"
    assert config.loco_api_key == "test-key-123"
    assert config.filters == ["ios", "common"]


def test_project_configuration_with_optional_none():
    """Test ProjectConfiguration with None for optional fields."""
    config = ProjectConfiguration(
        localizable_path="/path/to/localizable",
        main_target_localizable_path=None,
        loco_api_key="test-key",
        filters=[],
    )

    assert config.localizable_path == "/path/to/localizable"
    assert config.main_target_localizable_path is None
    assert config.loco_api_key == "test-key"
    assert config.filters == []


def test_ensure_config_file_exist_raises_error_for_missing_file():
    """Test that _ensure_config_file_exist raises LocoConfigError for missing file."""
    with pytest.raises(LocoConfigError) as exc_info:
        _ensure_config_file_exist("/nonexistent/path/to/config.yml")

    assert "Configuration file is missing" in str(exc_info.value)


def test_ensure_config_file_exist_succeeds_for_existing_file():
    """Test that _ensure_config_file_exist succeeds for existing file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write("test: value\n")
        temp_file = f.name

    try:
        _ensure_config_file_exist(temp_file)  # Should not raise
    finally:
        os.unlink(temp_file)


def test_read_config_returns_parsed_yaml():
    """Test that _read_config correctly parses YAML."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        config_data = {
            "project": "test-project",
            "api_key": "test-key",
            "paths": {"localizable": "/path/to/localizable"},
        }
        yaml.dump(config_data, f)
        temp_file = f.name

    try:
        config = _read_config(temp_file)
        assert config["project"] == "test-project"
        assert config["api_key"] == "test-key"
        assert config["paths"]["localizable"] == "/path/to/localizable"
    finally:
        os.unlink(temp_file)


def test_read_config_raises_error_for_invalid_yaml():
    """Test that _read_config raises LocoConfigError for invalid YAML."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write("invalid: yaml: content:\n  - malformed\n  unclosed: [bracket")
        temp_file = f.name

    try:
        with pytest.raises(LocoConfigError) as exc_info:
            _read_config(temp_file)
        assert "Invalid YAML" in str(exc_info.value)
    finally:
        os.unlink(temp_file)


def test_read_config_raises_error_for_missing_file():
    """Test that _read_config raises LocoConfigError for missing file."""
    with pytest.raises(LocoConfigError) as exc_info:
        _read_config("/nonexistent/config.yml")

    assert "Configuration file is missing" in str(exc_info.value)


def test_get_project_config_returns_config_dict():
    """Test that get_project_config returns configuration dictionary."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        config_data = {"project": "test", "key": "value"}
        yaml.dump(config_data, f)
        temp_file = f.name

    try:
        config = get_project_config(temp_file)
        assert config["project"] == "test"
        assert config["key"] == "value"
    finally:
        os.unlink(temp_file)
