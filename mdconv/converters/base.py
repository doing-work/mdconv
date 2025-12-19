"""Base converter interface and registry."""

from abc import ABC, abstractmethod
from typing import List, Optional, Type


class BaseConverter(ABC):
    """Abstract base class for format converters."""

    def __init__(self, pandoc_wrapper):
        """
        Initialize converter.

        Args:
            pandoc_wrapper: PandocWrapper instance
        """
        self.pandoc_wrapper = pandoc_wrapper

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the format name (e.g., 'html', 'pdf')."""
        pass

    @abstractmethod
    def convert(
        self,
        input_data: str,
        output_file: Optional[str] = None,
        **options,
    ) -> bytes:
        """
        Convert input data to this format.

        Args:
            input_data: Input content (string or file path)
            output_file: Optional output file path
            **options: Format-specific options

        Returns:
            Converted content as bytes if output_file is None
        """
        pass

    def validate_options(self, options: dict) -> dict:
        """
        Validate and normalize options for this format.

        Args:
            options: Raw options dictionary

        Returns:
            Validated and normalized options
        """
        return options


class ConverterRegistry:
    """Registry for format converters."""

    def __init__(self):
        """Initialize the registry."""
        self._converters: dict = {}

    def register(self, format_name: str, converter_class: Type[BaseConverter]):
        """
        Register a converter for a format.

        Args:
            format_name: Format name (e.g., 'html')
            converter_class: Converter class (subclass of BaseConverter)
        """
        self._converters[format_name.lower()] = converter_class

    def get(self, format_name: str) -> Optional[Type[BaseConverter]]:
        """
        Get converter class for a format.

        Args:
            format_name: Format name

        Returns:
            Converter class or None if not found
        """
        return self._converters.get(format_name.lower())

    def list_formats(self) -> List[str]:
        """List all registered format names."""
        return sorted(self._converters.keys())

    def has_format(self, format_name: str) -> bool:
        """Check if a format is registered."""
        return format_name.lower() in self._converters

