"""Tests for Windows and Linux platform implementations."""

import tempfile

import pytest

from import_loco.core.exceptions import LocoConfigError
from import_loco.core.parsers.resx_parser import ResxTranslationsParser
from import_loco.core.parsers.po_parser import PoTranslationsParser
from import_loco.platforms import get_platform, list_available_platforms
from import_loco.platforms.windows import WindowsPlatform
from import_loco.platforms.linux import LinuxPlatform


class TestWindowsPlatform:
    """Tests for WindowsPlatform."""

    def test_platform_name(self):
        """Test that platform name is correct."""
        platform = WindowsPlatform({})
        assert platform.name == "windows"

    def test_supported_languages_default(self):
        """Test that Windows returns default supported languages."""
        platform = WindowsPlatform({})
        languages = platform.get_supported_languages()
        assert isinstance(languages, list)
        assert "en" in languages
        assert "fr" in languages

    def test_supported_languages_from_config(self):
        """Test that Windows returns languages from config when provided."""
        config = {"languages": ["en", "de", "ja"]}
        platform = WindowsPlatform(config)
        languages = platform.get_supported_languages()
        assert languages == ["en", "de", "ja"]

    def test_get_translation_file_path_resx(self):
        """Test getting path for .resx file."""
        platform = WindowsPlatform({})
        path = platform.get_translation_file_path("/base/path", "en", "resx")
        assert path == "/base/path/Resources.resx"
        
        path_fr = platform.get_translation_file_path("/base/path", "fr", "resx")
        assert path_fr == "/base/path/Resources.fr.resx"

    def test_get_translation_file_path_unsupported_type(self):
        """Test that unsupported resource type raises ValueError."""
        platform = WindowsPlatform({})
        with pytest.raises(ValueError) as exc_info:
            platform.get_translation_file_path("/base/path", "en", "unsupported")
        assert "Unsupported resource type" in str(exc_info.value)

    def test_get_resource_types(self):
        """Test that Windows returns correct resource types."""
        platform = WindowsPlatform({})
        types = platform.get_resource_types()
        assert "resx" in types
        assert len(types) == 1

    def test_get_parser_for_resx(self):
        """Test getting parser for resx resource."""
        platform = WindowsPlatform({})
        parser = platform.get_parser_for_resource_type("resx")
        assert isinstance(parser, ResxTranslationsParser)

    def test_get_parser_unsupported_type(self):
        """Test that unsupported parser type raises ValueError."""
        platform = WindowsPlatform({})
        with pytest.raises(ValueError):
            platform.get_parser_for_resource_type("unsupported")

    def test_get_loco_filters_resx(self):
        """Test getting Loco filters for resx."""
        platform = WindowsPlatform({})
        filters = platform.get_loco_filters("resx")
        assert filters == ["windows"]

    def test_get_archive_endpoint_resx(self):
        """Test getting archive endpoint for resx."""
        platform = WindowsPlatform({})
        endpoint = platform.get_archive_endpoint("resx")
        assert endpoint == "resx.zip"

    def test_validate_configuration_missing_field(self):
        """Test configuration validation with missing required field."""
        platform = WindowsPlatform({})
        config = {"localizable_path": "/path/to/resources"}
        
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
            platform = WindowsPlatform(config)
            
            # Should not raise
            platform.validate_configuration(config)


class TestLinuxPlatform:
    """Tests for LinuxPlatform."""

    def test_platform_name(self):
        """Test that platform name is correct."""
        platform = LinuxPlatform({})
        assert platform.name == "linux"

    def test_supported_languages_default(self):
        """Test that Linux returns default supported languages."""
        platform = LinuxPlatform({})
        languages = platform.get_supported_languages()
        assert isinstance(languages, list)
        assert "en" in languages

    def test_supported_languages_from_config(self):
        """Test that Linux returns languages from config when provided."""
        config = {"languages": ["en", "es", "pt"]}
        platform = LinuxPlatform(config)
        languages = platform.get_supported_languages()
        assert languages == ["en", "es", "pt"]

    def test_get_translation_file_path_po(self):
        """Test getting path for .po file."""
        platform = LinuxPlatform({})
        path = platform.get_translation_file_path("/base/path", "en", "po")
        assert path == "/base/path/en/LC_MESSAGES/messages.po"

    def test_get_translation_file_path_po_with_custom_domain(self):
        """Test getting path for .po file with custom domain."""
        config = {"domain": "myapp"}
        platform = LinuxPlatform(config)
        path = platform.get_translation_file_path("/base/path", "fr", "po")
        assert path == "/base/path/fr/LC_MESSAGES/myapp.po"

    def test_get_translation_file_path_unsupported_type(self):
        """Test that unsupported resource type raises ValueError."""
        platform = LinuxPlatform({})
        with pytest.raises(ValueError) as exc_info:
            platform.get_translation_file_path("/base/path", "en", "unsupported")
        assert "Unsupported resource type" in str(exc_info.value)

    def test_get_resource_types(self):
        """Test that Linux returns correct resource types."""
        platform = LinuxPlatform({})
        types = platform.get_resource_types()
        assert "po" in types
        assert len(types) == 1

    def test_get_parser_for_po(self):
        """Test getting parser for po resource."""
        platform = LinuxPlatform({})
        parser = platform.get_parser_for_resource_type("po")
        assert isinstance(parser, PoTranslationsParser)

    def test_get_parser_unsupported_type(self):
        """Test that unsupported parser type raises ValueError."""
        platform = LinuxPlatform({})
        with pytest.raises(ValueError):
            platform.get_parser_for_resource_type("unsupported")

    def test_get_loco_filters_po(self):
        """Test getting Loco filters for po."""
        platform = LinuxPlatform({})
        filters = platform.get_loco_filters("po")
        assert filters == ["linux"]

    def test_get_archive_endpoint_po(self):
        """Test getting archive endpoint for po."""
        platform = LinuxPlatform({})
        endpoint = platform.get_archive_endpoint("po")
        assert endpoint == "po.zip"

    def test_validate_configuration_missing_field(self):
        """Test configuration validation with missing required field."""
        platform = LinuxPlatform({})
        config = {"localizable_path": "/path/to/locale"}
        
        with pytest.raises(LocoConfigError) as exc_info:
            platform.validate_configuration(config)
        
        assert "loco_api_key" in str(exc_info.value)

    def test_validate_configuration_valid(self):
        """Test configuration validation with valid config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "localizable_path": tmpdir,
                "loco_api_key": "test-key-456",
            }
            platform = LinuxPlatform(config)
            
            # Should not raise
            platform.validate_configuration(config)


class TestPlatformRegistryWithNewPlatforms:
    """Tests for platform registry with Windows and Linux."""

    def test_get_platform_windows(self):
        """Test getting Windows platform instance."""
        config = {"platform": "windows", "loco_api_key": "test"}
        platform = get_platform("windows", config)
        assert isinstance(platform, WindowsPlatform)
        assert platform.name == "windows"

    def test_get_platform_linux(self):
        """Test getting Linux platform instance."""
        config = {"platform": "linux", "loco_api_key": "test"}
        platform = get_platform("linux", config)
        assert isinstance(platform, LinuxPlatform)
        assert platform.name == "linux"

    def test_list_available_platforms_includes_all(self):
        """Test that all platforms are listed."""
        platforms = list_available_platforms()
        assert "ios" in platforms
        assert "macos" in platforms
        assert "windows" in platforms
        assert "linux" in platforms
        assert len(platforms) == 4
