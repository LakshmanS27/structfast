"""Custom exceptions used across the package."""


class StructifyError(Exception):
    """Base exception for all structify errors."""


class ParseError(StructifyError):
    """Raised when structure input cannot be parsed safely."""


class BuildError(StructifyError):
    """Raised when the filesystem builder cannot complete an action."""


class ClipboardError(StructifyError):
    """Raised when clipboard access fails."""
