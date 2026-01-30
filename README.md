# Import Loco

Your friendly neighborhood localization importer! A modern Python CLI tool that fetches your localized strings
from [Loco](https://localise.biz/) and drops them right into your iOS, macOS, or Windows project. No fuss, no muss.

## What's in the Box?

- **Multi-Platform Love**: iOS, macOS, and Windows are all invited to the party
- **All the Formats**: `.strings`, `.stringsdict`, and `.resx` — we speak your language(s)
- **Validation Superpowers**: Catches typos, wrong punctuation, and those sneaky straight apostrophes before they reach production
- **YAML Config**: Because life's too short for INI files
- **Secure by Default**: API keys stay safe in env vars or separate files

## Quick Start

### 1. Install

## With mise

```bash
mise install pipx@latest
pipx install pipx:infomaniak/importloco
```

### 2. Configure

Create `.import_loco.yml` in your project root:

```yaml
platform: ios
localizable_path: /path/to/your/Resources
languages: [ en, fr, de, es, it ]
```

### 3. Set Your API Key

Pick your favorite method:

```bash
# Environment variable (great for CI/CD)
export LOCO_API_KEY="your-api-key"

# Or a dedicated file (nice for local dev)
echo "your-api-key" > .import_loco_api
```

### 4. Import!

```bash
import_loco                            # Import everything
import_loco -r strings                 # Just .strings files
import_loco -r strings -r stringsdict  # .strings and .stringsdict files
import_loco -c                         # Validate only (no import)
import_loco -v                         # Verbose mode for the curious
```

## Platform Support

| Platform | Resource Types                                               | File Format            | Path Pattern                   |
|----------|--------------------------------------------------------------|------------------------|--------------------------------|
| iOS      | `strings`, `stringsdict`, `infoplist`, `main_target_strings` | .strings, .stringsdict | `en.lproj/Localizable.strings` |
| macOS    | `strings`, `stringsdict`                                     | .strings, .stringsdict | `en.lproj/Localizable.strings` |
| Windows  | `resx`                                                       | .resx                  | `Resources.en.resx`            |

## Configuration examples

### iOS

```yaml
platform: ios
localizable_path: /path/to/Resources
main_target_localizable_path: /path/to/MainTarget  # For InfoPlist.strings
languages: [ en, fr, de, es, it ]
filters: [ common ]  # Optional additional Loco tag filters
```

### macOS

```yaml
platform: macos
localizable_path: /path/to/Resources
languages: [ en, fr, de, es, it ]
```

### All Configuration Options

| Option                         | Required | Description                                               |
|--------------------------------|----------|-----------------------------------------------------------|
| `platform`                     | No       | `ios` (default), `macos`, or `windows`                    |
| `localizable_path`             | Yes      | Path to your localization files                           |
| `main_target_localizable_path` | No       | iOS only: path for InfoPlist.strings                      |
| `languages`                    | No       | List of language codes (defaults to `de, en, es, fr, it`) |
| `filters`                      | No       | Additional Loco tag filters to include                    |

## Validation

Run `-c` to check your translations without importing:

```bash
import_loco -c
```

The validator catches common localization issues:

- **Global rules**: Straight apostrophes (`'` → `'`), wrong ellipsis (`...` → `…`), trailing spaces
- **English**: No space before `:`, `?`, `!`
- **French**: Space before `:`, `?`, `!` and proper email formatting
- **German**: Currency symbols, specific terminology
- **Italian/Spanish**: Terminology consistency, punctuation rules

Validation errors show the language, string ID, and exactly what's wrong — so you can fix them before your users notice.

## Development

```bash
# Install dev dependencies
pdm install

# Run tests
pdm run pytest

# Lint
pdm run ruff check
```

### Requirements

- Python 3.9+
- requests >= 2.32.5
- pyyaml >= 6.0.3

## Troubleshooting

**"Configuration file not found"**
→ Create `.import_loco.yml` in your project root

**"API key missing"**
→ Set `LOCO_API_KEY` env var or create `.import_loco_api` file

**"Unsupported platform"**
→ Use `ios`, `macos`, or `windows`

**"Resource type not supported"**
→ Check the platform table above for valid resource types

## Credits

Crafted with care by the iOS team at [Infomaniak](https://www.infomaniak.com/) in Geneva, Switzerland.

Inspired by [Ink](https://github.com/Infomaniak/ink_utils).

Licensed under Apache 2.0.

---

Fin ! The End! Fine! Fin! Ende!
