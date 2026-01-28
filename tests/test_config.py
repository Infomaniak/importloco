"""Tests for configuration loading."""

import os
import tempfile

import pytest
import yaml

from import_loco.core.config.config import (
    get_project_config,
    _read_config,
    _ensure_config_file_exist,
    _load_api_key,
)
from import_loco.core.exceptions import LocoConfigError


def test_load_api_key_from_environment(monkeypatch):
    """Test loading API key from environment variable."""
    monkeypatch.setenv("LOCO_API_KEY", "env-api-key")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, ".import_loco.yml")
        api_key = _load_api_key(config_file)
        
        assert api_key == "env-api-key"


def test_load_api_key_from_file():
    """Test loading API key from .import_loco_api file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, ".import_loco.yml")
        api_key_file = os.path.join(tmpdir, ".import_loco_api")
        
        with open(api_key_file, "w") as f:
            f.write("file-api-key")
        
        api_key = _load_api_key(config_file)
        assert api_key == "file-api-key"


def test_load_api_key_env_takes_priority(monkeypatch):
    """Test that environment variable takes priority over file."""
    monkeypatch.setenv("LOCO_API_KEY", "env-api-key")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, ".import_loco.yml")
        api_key_file = os.path.join(tmpdir, ".import_loco_api")
        
        with open(api_key_file, "w") as f:
            f.write("file-api-key")
        
        api_key = _load_api_key(config_file)
        assert api_key == "env-api-key"


def test_load_api_key_returns_none_when_not_found():
    """Test that _load_api_key returns None when no key is found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, ".import_loco.yml")
        api_key = _load_api_key(config_file)
        
        assert api_key is None


def test_get_project_config_with_api_key_from_file():
    """Test that get_project_config loads API key from file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, ".import_loco.yml")
        api_key_file = os.path.join(tmpdir, ".import_loco_api")
        
        with open(config_file, "w") as f:
            yaml.dump({"platform": "ios", "localizable_path": "/tmp"}, f)
        
        with open(api_key_file, "w") as f:
            f.write("test-api-key")
        
        config = get_project_config(config_file)
        
        assert config["loco_api_key"] == "test-api-key"


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
