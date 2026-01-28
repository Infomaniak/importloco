"""Tests for Windows and Linux parsers."""

import os
import tempfile

import pytest

from import_loco.core.exceptions import LocoParserError
from import_loco.core.parsers.resx_parser import ResxTranslationsParser
from import_loco.core.parsers.po_parser import PoTranslationsParser


class TestResxTranslationsParser:
    """Tests for ResxTranslationsParser."""

    def test_parse_simple_resx_file(self):
        """Test parsing a simple .resx file."""
        parser = ResxTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".resx", delete=False, encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write('<root>\n')
            f.write('  <data name="HelloWorld" xml:space="preserve">\n')
            f.write('    <value>Hello World</value>\n')
            f.write('  </data>\n')
            f.write('  <data name="Goodbye" xml:space="preserve">\n')
            f.write('    <value>Goodbye</value>\n')
            f.write('  </data>\n')
            f.write('</root>\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert data["HelloWorld"] == "Hello World"
            assert data["Goodbye"] == "Goodbye"
            assert len(data) == 2
        finally:
            os.unlink(temp_file)

    def test_parse_resx_with_empty_value(self):
        """Test parsing .resx file with empty value."""
        parser = ResxTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".resx", delete=False, encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write('<root>\n')
            f.write('  <data name="EmptyKey" xml:space="preserve">\n')
            f.write('    <value></value>\n')
            f.write('  </data>\n')
            f.write('</root>\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert "EmptyKey" in data
            assert data["EmptyKey"] == ""
        finally:
            os.unlink(temp_file)

    def test_parse_resx_raises_error_for_missing_file(self):
        """Test that parser raises LocoParserError for missing file."""
        parser = ResxTranslationsParser()
        
        with pytest.raises(LocoParserError) as exc_info:
            parser.parse("/nonexistent/file.resx")
        
        assert "not found" in str(exc_info.value)

    def test_parse_resx_raises_error_for_invalid_xml(self):
        """Test that parser raises LocoParserError for invalid XML."""
        parser = ResxTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".resx", delete=False, encoding="utf-8") as f:
            f.write('<invalid><xml><structure>')
            temp_file = f.name

        try:
            with pytest.raises(LocoParserError) as exc_info:
                parser.parse(temp_file)
            assert "Invalid XML" in str(exc_info.value)
        finally:
            os.unlink(temp_file)


class TestPoTranslationsParser:
    """Tests for PoTranslationsParser."""

    def test_parse_simple_po_file(self):
        """Test parsing a simple .po file."""
        parser = PoTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".po", delete=False, encoding="utf-8") as f:
            f.write('# Translation file\n')
            f.write('msgid ""\n')
            f.write('msgstr ""\n')
            f.write('\n')
            f.write('msgid "hello"\n')
            f.write('msgstr "Hallo"\n')
            f.write('\n')
            f.write('msgid "world"\n')
            f.write('msgstr "Welt"\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert data["hello"] == "Hallo"
            assert data["world"] == "Welt"
            assert len(data) == 2  # Empty msgid should be removed
        finally:
            os.unlink(temp_file)

    def test_parse_po_with_multiline_strings(self):
        """Test parsing .po file with multi-line strings."""
        parser = PoTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".po", delete=False, encoding="utf-8") as f:
            f.write('msgid ""\n')
            f.write('"This is a long "\n')
            f.write('"multi-line string"\n')
            f.write('msgstr ""\n')
            f.write('"Das ist ein langer "\n')
            f.write('"mehrzeiliger String"\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert "This is a long multi-line string" in data
            assert data["This is a long multi-line string"] == "Das ist ein langer mehrzeiliger String"
        finally:
            os.unlink(temp_file)

    def test_parse_po_with_escape_sequences(self):
        """Test parsing .po file with escape sequences."""
        parser = PoTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".po", delete=False, encoding="utf-8") as f:
            f.write('msgid "line1\\nline2"\n')
            f.write('msgstr "Zeile1\\nZeile2"\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert "line1\nline2" in data
            assert data["line1\nline2"] == "Zeile1\nZeile2"
        finally:
            os.unlink(temp_file)

    def test_parse_po_raises_error_for_missing_file(self):
        """Test that parser raises LocoParserError for missing file."""
        parser = PoTranslationsParser()
        
        with pytest.raises(LocoParserError) as exc_info:
            parser.parse("/nonexistent/file.po")
        
        assert "not found" in str(exc_info.value)

    def test_parse_empty_po_file(self):
        """Test parsing an empty .po file."""
        parser = PoTranslationsParser()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".po", delete=False, encoding="utf-8") as f:
            f.write('# Empty file\n')
            temp_file = f.name

        try:
            data = parser.parse(temp_file)
            assert len(data) == 0
        finally:
            os.unlink(temp_file)
