"""Tests for platform implementations."""

import os
import tempfile

import pytest

from import_loco.core.exceptions import LocoConfigError
from import_loco.core.parsers.apple_translations_parser import (
    StringsTranslationsParser,
    StringsDictTranslationsParser,
)
from import_loco.platforms import get_platform, list_available_platforms
from import_loco.platforms.ios import IOSPlatform
from import_loco.platforms.macos import MacOSPlatform


class TestIOSPlatform:
    """Tests for IOSPlatform."""

    def test_platform_name(self):
        """Test that platform name is correct."""
        platform = IOSPlatform({})
        assert platform.name == "ios"

    def test_supported_languages_default(self):
        """Test that iOS returns default supported languages."""
        platform = IOSPlatform({})
        languages = platform.get_supported_languages()
        assert isinstance(languages, list)
        assert "en" in languages
        assert "fr" in languages

    def test_supported_languages_from_config(self):
        """Test that iOS returns languages from config when provided."""
        config = {"languages": ["en", "de", "ja"]}
        platform = IOSPlatform(config)
        languages = platform.get_supported_languages()
        assert languages == ["en", "de", "ja"]

    def test_get_translation_file_path_strings(self):
        """Test getting path for .strings file."""
        platform = IOSPlatform({})
        path = platform.get_translation_file_path("/base/path", "en", "strings")
        assert path == "/base/path/en.lproj/Localizable.strings"

    def test_get_translation_file_path_stringsdict(self):
        """Test getting path for .stringsdict file."""
        platform = IOSPlatform({})
        path = platform.get_translation_file_path("/base/path", "fr", "stringsdict")
        assert path == "/base/path/fr.lproj/Localizable.stringsdict"

    def test_get_translation_file_path_infoplist(self):
        """Test getting path for InfoPlist.strings file."""
        platform = IOSPlatform({})
        path = platform.get_translation_file_path("/base/path", "de", "infoplist")
        assert path == "/base/path/de.lproj/InfoPlist.strings"

    def test_get_translation_file_path_unsupported_type(self):
        """Test that unsupported resource type raises ValueError."""
        platform = IOSPlatform({})
        with pytest.raises(ValueError) as exc_info:
            platform.get_translation_file_path("/base/path", "en", "unsupported")
        assert "Unsupported resource type" in str(exc_info.value)

    def test_get_resource_types(self):
        """Test that iOS returns correct resource types."""
        platform = IOSPlatform({})
        types = platform.get_resource_types()
        assert "strings" in types
        assert "stringsdict" in types
        assert "infoplist" in types

    def test_get_parser_for_strings(self):
        """Test getting parser for strings resource."""
        platform = IOSPlatform({})
        parser = platform.get_parser_for_resource_type("strings")
        assert isinstance(parser, StringsTranslationsParser)

    def test_get_parser_for_stringsdict(self):
        """Test getting parser for stringsdict resource."""
        platform = IOSPlatform({})
        parser = platform.get_parser_for_resource_type("stringsdict")
        assert isinstance(parser, StringsDictTranslationsParser)

    def test_get_parser_for_infoplist(self):
        """Test getting parser for infoplist resource."""
        platform = IOSPlatform({})
        parser = platform.get_parser_for_resource_type("infoplist")
        assert isinstance(parser, StringsTranslationsParser)

    def test_get_parser_unsupported_type(self):
        """Test that unsupported parser type raises ValueError."""
        platform = IOSPlatform({})
        with pytest.raises(ValueError):
            platform.get_parser_for_resource_type("unsupported")

    def test_get_loco_filters_strings(self):
        """Test getting Loco filters for strings."""
        platform = IOSPlatform({})
        filters = platform.get_loco_filters("strings")
        assert filters == ["ios"]

    def test_get_loco_filters_stringsdict(self):
        """Test getting Loco filters for stringsdict."""
        platform = IOSPlatform({})
        filters = platform.get_loco_filters("stringsdict")
        assert filters == ["ios-stringsdict"]

    def test_get_archive_endpoint_strings(self):
        """Test getting archive endpoint for strings."""
        platform = IOSPlatform({})
        endpoint = platform.get_archive_endpoint("strings")
        assert endpoint == "strings.zip"

    def test_get_archive_endpoint_stringsdict(self):
        """Test getting archive endpoint for stringsdict."""
        platform = IOSPlatform({})
        endpoint = platform.get_archive_endpoint("stringsdict")
        assert endpoint == "stringsdict.zip"

    def test_validate_configuration_missing_field(self):
        """Test configuration validation with missing required field."""
        platform = IOSPlatform({})
        config = {"localizable_path": "/path/to/localizable"}
        
        with pytest.raises(LocoConfigError) as exc_info:
            platform.validate_configuration(config)
        
        assert "loco_api_key" in str(exc_info.value)

    def test_validate_configuration_valid(self):
        """Test configuration validation with valid config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "localizable_path": tmpdir,
                "loco_api_key": "test-key-123",
            }
            platform = IOSPlatform(config)
            
            # Should not raise
            platform.validate_configuration(config)


class TestMacOSPlatform:
    """Tests for MacOSPlatform."""

    def test_platform_name(self):
        """Test that platform name is correct."""
        platform = MacOSPlatform({})
        assert platform.name == "macos"

    def test_supported_languages(self):
        """Test that macOS returns supported languages."""
        platform = MacOSPlatform({})
        languages = platform.get_supported_languages()
        assert isinstance(languages, list)
        assert "en" in languages

    def test_get_translation_file_path(self):
        """Test getting path for translation file."""
        platform = MacOSPlatform({})
        path = platform.get_translation_file_path("/base/path", "en", "strings")
        assert path == "/base/path/en.lproj/Localizable.strings"

    def test_get_resource_types(self):
        """Test that macOS returns correct resource types."""
        platform = MacOSPlatform({})
        types = platform.get_resource_types()
        assert "strings" in types
        assert "stringsdict" in types
        assert "infoplist" not in types  # macOS doesn't support infoplist

    def test_get_loco_filters_strings(self):
        """Test getting Loco filters for strings."""
        platform = MacOSPlatform({})
        filters = platform.get_loco_filters("strings")
        assert filters == ["macos"]

    def test_validate_configuration_valid(self):
        """Test configuration validation with valid config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "localizable_path": tmpdir,
                "loco_api_key": "test-key-456",
            }
            platform = MacOSPlatform(config)
            
            # Should not raise
            platform.validate_configuration(config)


class TestPlatformRegistry:
    """Tests for platform registry and factory."""

    def test_get_platform_ios(self):
        """Test getting iOS platform instance."""
        config = {"platform": "ios", "loco_api_key": "test"}
        platform = get_platform("ios", config)
        assert isinstance(platform, IOSPlatform)
        assert platform.name == "ios"

    def test_get_platform_macos(self):
        """Test getting macOS platform instance."""
        config = {"platform": "macos", "loco_api_key": "test"}
        platform = get_platform("macos", config)
        assert isinstance(platform, MacOSPlatform)
        assert platform.name == "macos"

    def test_get_platform_case_insensitive(self):
        """Test that platform name is case-insensitive."""
        config = {"loco_api_key": "test"}
        platform1 = get_platform("iOS", config)
        platform2 = get_platform("IOS", config)
        platform3 = get_platform("ios", config)
        
        assert all(isinstance(p, IOSPlatform) for p in [platform1, platform2, platform3])

    def test_get_platform_unsupported(self):
        """Test that unsupported platform raises LocoConfigError."""
        with pytest.raises(LocoConfigError) as exc_info:
            get_platform("unsupported", {})
        
        assert "Unsupported platform" in str(exc_info.value)
        assert "Available platforms" in str(exc_info.value)

    def test_list_available_platforms(self):
        """Test listing all available platforms."""
        platforms = list_available_platforms()
        assert "ios" in platforms
        assert "macos" in platforms
        assert isinstance(platforms, list)
