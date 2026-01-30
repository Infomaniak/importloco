# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Import Loco is a Python CLI tool for importing localized strings from Loco (localise.biz) into iOS, macOS, Windows, and Linux projects. It handles multiple file formats (.strings, .stringsdict, .resx, .po) and includes a validation system for localization quality.

## Commands

```bash
# Install dependencies
pdm install

# Run the tool
python -m import_loco              # Import all resources
python -m import_loco -r strings   # Import specific resource type
python -m import_loco -c           # Validate without importing
python -m import_loco -v           # Verbose mode

# Lint
pdm run ruff check

# Run tests
pdm run pytest
```

## Architecture

### Platform Abstraction (`src/import_loco/core/platforms/`)
Abstract `Platform` base class with concrete implementations for each OS. Each platform defines:
- Supported resource types and file formats
- Loco API filters for fetching translations
- Source/destination file path mappings

Platforms: `ios.py`, `macos.py`, `windows.py` (Linux partial support)

### Parser Strategy (`src/import_loco/core/parsers/`)
`TranslationsParser` base class with format-specific implementations:
- `StringsTranslationsParser` - Apple .strings files
- `StringsDictTranslationsParser` - Apple .stringsdict (plurals)
- `ResxTranslationsParser` - Windows .resx XML

### Validation Rules (`src/loco_validator/`)
Rule-based system for localization quality checks. Rules can be global or language-specific. Each rule supports exception IDs to exclude specific strings.

**Note:** This directory is excluded from Ruff linting (see pyproject.toml).

### Configuration
- `.import_loco.yml` - Project config (platform, paths, languages, filters)
- `.import_loco_api` - API key file (local dev)
- `LOCO_API_KEY` env var - API key (CI/CD)

### Module Structure
- `src/import_loco/cli_tool/` - CLI entry point and argument parsing
- `src/import_loco/core/config/` - Configuration loading
- `src/import_loco/core/loco/` - Loco API integration (fetch, import, validate)
- `src/import_loco/core/exceptions.py` - Domain-specific exceptions
- `src/import_loco/helpers/constants.py` - Shared constants

## Code Style

- Line length: 130 characters
- Linter: Ruff (ignores F403, F405 for wildcard imports)
- Python: 3.9+
