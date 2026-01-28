"""Tests for translation parsers."""

import os
import tempfile

import pytest

from import_loco.core.exceptions import LocoParserError
from import_loco.core.parsers.apple_translations_parser import (
    StringsTranslationsParser,
    StringsDictTranslationsParser,
)


class TestStringsTranslationsParser:
    """Tests for StringsTranslationsParser."""

    def test_parse_simple_strings_file(self):
        """Test parsing a simple .strings file."""
        parser = StringsTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".strings", delete=False, encoding="utf-8") as f:
            f.write('"hello" = "Hello";\n')
            f.write('"world" = "World";\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert data["hello"] == "Hello"
            assert data["world"] == "World"
            assert len(data) == 2
        finally:
            os.unlink(temp_file)

    def test_parse_strings_with_special_characters(self):
        """Test parsing strings with special characters."""
        parser = StringsTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".strings", delete=False, encoding="utf-8") as f:
            f.write('"key.with.dots" = "Value with spaces";\n')
            f.write('"key_with_underscores" = "Value with special: chars!";\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert data["key.with.dots"] == "Value with spaces"
            assert data["key_with_underscores"] == "Value with special: chars!"
        finally:
            os.unlink(temp_file)

    def test_parse_strings_skips_comments(self):
        """Test that parser handles comment lines."""
        parser = StringsTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".strings", delete=False, encoding="utf-8") as f:
            f.write('// This is a comment\n')
            f.write('"key1" = "Value 1";\n')
            f.write('/* Multi-line\n')
            f.write('   comment */\n')
            f.write('"key2" = "Value 2";\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert data["key1"] == "Value 1"
            assert data["key2"] == "Value 2"
            assert len(data) == 2
        finally:
            os.unlink(temp_file)

    def test_parse_strings_raises_error_for_missing_file(self):
        """Test that parser raises LocoParserError for missing file."""
        parser = StringsTranslationsParser()
        
        with pytest.raises(LocoParserError) as exc_info:
            parser.parse("/nonexistent/file.strings")
        
        assert "not found" in str(exc_info.value)

    def test_parse_empty_strings_file(self):
        """Test parsing an empty .strings file."""
        parser = StringsTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".strings", delete=False, encoding="utf-8") as f:
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert len(data) == 0
        finally:
            os.unlink(temp_file)


class TestStringsDictTranslationsParser:
    """Tests for StringsDictTranslationsParser."""

    def test_parse_simple_stringsdict_file(self):
        """Test parsing a simple .stringsdict file."""
        parser = StringsDictTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".stringsdict", delete=False, encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
            f.write('<plist version="1.0">\n')
            f.write('<dict>\n')
            f.write('  <key>items_count</key>\n')
            f.write('  <dict>\n')
            f.write('    <key>NSStringLocalizedFormatKey</key>\n')
            f.write('    <string>%#@items@</string>\n')
            f.write('    <key>items</key>\n')
            f.write('    <dict>\n')
            f.write('      <key>NSStringFormatSpecTypeKey</key>\n')
            f.write('      <string>NSStringPluralRuleType</string>\n')
            f.write('      <key>NSStringFormatValueTypeKey</key>\n')
            f.write('      <string>d</string>\n')
            f.write('      <key>zero</key>\n')
            f.write('      <string>No items</string>\n')
            f.write('      <key>one</key>\n')
            f.write('      <string>One item</string>\n')
            f.write('      <key>other</key>\n')
            f.write('      <string>%d items</string>\n')
            f.write('    </dict>\n')
            f.write('  </dict>\n')
            f.write('</dict>\n')
            f.write('</plist>\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert "items_count-zero" in data
            assert data["items_count-zero"] == "No items"
            assert "items_count-one" in data
            assert data["items_count-one"] == "One item"
            assert "items_count-other" in data
            assert data["items_count-other"] == "%d items"
        finally:
            os.unlink(temp_file)

    def test_parse_stringsdict_raises_error_for_missing_file(self):
        """Test that parser raises LocoParserError for missing file."""
        parser = StringsDictTranslationsParser()
        
        with pytest.raises(LocoParserError) as exc_info:
            parser.parse("/nonexistent/file.stringsdict")
        
        assert "not found" in str(exc_info.value)

    def test_parse_stringsdict_raises_error_for_invalid_xml(self):
        """Test that parser raises LocoParserError for invalid XML."""
        parser = StringsDictTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".stringsdict", delete=False, encoding="utf-8") as f:
            f.write('<invalid><xml><structure>')
            temp_file = f.name

        try:
            with pytest.raises(LocoParserError) as exc_info:
                parser.parse(temp_file)
            assert "Invalid XML" in str(exc_info.value)
        finally:
            os.unlink(temp_file)

    def test_parse_stringsdict_raises_error_for_missing_root_dict(self):
        """Test that parser raises LocoParserError when root dict is missing."""
        parser = StringsDictTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".stringsdict", delete=False, encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<plist version="1.0">\n')
            f.write('</plist>\n')
            temp_file = f.name

        try:
            with pytest.raises(LocoParserError) as exc_info:
                parser.parse(temp_file)
            assert "missing root dict" in str(exc_info.value)
        finally:
            os.unlink(temp_file)
