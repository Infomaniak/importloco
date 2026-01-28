"""Custom exception classes for import_loco.

This module defines custom exceptions used throughout the import_loco application
to provide clear and specific error handling for different failure scenarios.
"""


class LocoError(Exception):
    """Base exception class for all import_loco errors."""

    pass


class LocoConfigError(LocoError):
    """Raised when there is an issue with configuration files or settings.

    This includes missing configuration files, invalid configuration values,
    or malformed configuration data.
    """

    pass


class LocoNetworkError(LocoError):
    """Raised when there is an issue with network operations.

    This includes API request failures, connection timeouts, or invalid responses
    from the Loco API.
    """

    pass


class LocoParserError(LocoError):
    """Raised when there is an issue parsing translation files.

    This includes malformed .strings files, invalid XML in .stringsdict files,
    or other file format parsing errors.
    """

    pass


class LocoValidationError(LocoError):
    """Raised when validation of translation strings fails.

    This includes format string mismatches, invalid placeholders, or other
    validation issues with translation content.
    """

    pass
