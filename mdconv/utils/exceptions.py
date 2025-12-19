"""Custom exceptions for mdconv."""

from typing import List


class MDConvError(Exception):
    """Base exception for all mdconv errors."""

    pass


class PandocNotFoundError(MDConvError):
    """Raised when pandoc is not found on the system."""

    def __init__(self):
        super().__init__(
            "Pandoc is not installed or not found in PATH. "
            "Install via pip: pip install pypandoc-binary "
            "or install manually from https://pandoc.org/installing.html"
        )


class InvalidFormatError(MDConvError):
    """Raised when an invalid output format is specified."""

    def __init__(self, format_name: str, available_formats: List[str]):
        self.format_name = format_name
        self.available_formats = available_formats
        super().__init__(
            f"Invalid format '{format_name}'. "
            f"Available formats: {', '.join(available_formats)}"
        )


class ConversionError(MDConvError):
    """Raised when a conversion fails."""

    def __init__(self, message: str, stderr: str = ""):
        self.stderr = stderr
        full_message = message
        if stderr:
            full_message += f"\nError details: {stderr}"
        super().__init__(full_message)

