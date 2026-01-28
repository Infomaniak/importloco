# Import Loco

A modern, multi-platform Python CLI tool for importing localized strings from [Loco](https://localise.biz/) translation management platform into iOS, macOS, Windows, and Linux projects.

## Features

- 🌍 **Multi-Platform Support**: iOS, macOS, Windows, and Linux
- 📝 **Multiple File Formats**: .strings, .stringsdict, .resx, .po
- ⚙️ **Flexible Configuration**: YAML-based with environment variable support
- 🔒 **Secure API Key Management**: Separate file or environment variable
- ✨ **Modern Python**: Type hints, comprehensive logging, and error handling
- 🧪 **Well-Tested**: >80% test coverage with 102+ tests

## Quick Start

### 1. Create Configuration

Create `.import_loco.yml` in your project root:
```yaml
platform: ios
localizable_path: /path/to/Resources
languages: [en, fr, de]
```

### 2. Set API Key

Choose one method:
```bash
# Environment variable (recommended for CI/CD)
export LOCO_API_KEY="your-api-key"

# Or create .import_loco_api file (recommended for local dev)
echo "your-api-key" > .import_loco_api
```

### 3. Run Import

```bash
python -m import_loco         # Import all resources
python -m import_loco -v      # Verbose mode
python -m import_loco -r strings  # Import specific resource
```

## Platform Support

| Platform | File Format | Example Path |
|----------|-------------|--------------|
| iOS | .strings, .stringsdict | en.lproj/Localizable.strings |
| macOS | .strings, .stringsdict | en.lproj/Localizable.strings |
| Windows | .resx | Resources.en.resx |
| Linux | .po | en/LC_MESSAGES/messages.po |

## Configuration Examples

### iOS/macOS
```yaml
platform: ios
localizable_path: /path/to/Resources
main_target_localizable_path: /path/to/MainTarget  # iOS only
languages: [en, fr, de, es]
filters: [common]  # Optional Loco filters
```

### Windows
```yaml
platform: windows
localizable_path: /path/to/Resources
languages: [en, fr, de]
```

### Linux
```yaml
platform: linux
localizable_path: /path/to/locale
domain: myapp  # Optional, defaults to "messages"
languages: [en, fr, de]
```

## API Key Priority

1. Environment variable `LOCO_API_KEY`
2. File `.import_loco_api` (in same directory as config)
3. Config file field `loco_api_key`

## Command-Line Options

```
python -m import_loco [OPTIONS]

Options:
  -r, --resource TYPE    Import specific resource type
  -c, --check           Validate without importing
  -v, --verbose         Enable debug logging
  -h, --help           Show help
```

## Installation

```bash
git clone https://github.com/Infomaniak/importloco.git
cd importloco
pip install -e .
```

### Requirements
- Python 3.9+
- requests>=2.32.5
- pyyaml>=6.0.3

## Development

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/import_loco

# Linting
python -m ruff check src/import_loco/
```

## Migration from Old Format

### Old (`.import_loco`)
```ini
[project]
localizable_path = /path
loco_key = xxx
```

### New (`.import_loco.yml`)
```yaml
platform: ios
localizable_path: /path
# Move API key to .import_loco_api file
```

## Troubleshooting

**Configuration file not found**
- Create `.import_loco.yml` in project root

**API key missing**
- Set `LOCO_API_KEY` env var or create `.import_loco_api` file

**Unsupported platform**
- Use: `ios`, `macos`, `windows`, or `linux`

## Credits

Designed by the iOS team at Infomaniak in Geneva, Switzerland.

Inspired by [Ink](https://github.com/Infomaniak/ink_utils).

---

Fin ! The End! Fine! Fin! Ende!
