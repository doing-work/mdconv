"""Main converter class."""

from pathlib import Path
from typing import List, Optional, Union

from mdconv.converters import registry
from mdconv.core.pandoc_wrapper import PandocWrapper
from mdconv.utils.exceptions import InvalidFormatError
from mdconv.utils.validation import validate_file_exists, validate_output_directory


class Converter:
    """Main converter class for converting markdown to various formats."""

    def __init__(self, pandoc_path: Optional[str] = None):
        """
        Initialize the converter.

        Args:
            pandoc_path: Optional path to pandoc executable
        """
        self.pandoc_wrapper = PandocWrapper(pandoc_path)
        self.registry = registry

    def convert(
        self,
        input_file: Union[str, Path],
        output_format: str,
        output_file: Optional[Union[str, Path]] = None,
        **options,
    ) -> Optional[bytes]:
        """
        Convert a markdown file to another format.

        Args:
            input_file: Path to input markdown file
            output_format: Target format (e.g., 'html', 'pdf', 'docx')
            output_file: Optional output file path. If None, returns bytes.
            **options: Format-specific options

        Returns:
            Converted content as bytes if output_file is None, otherwise None

        Raises:
            InvalidFormatError: If output_format is not supported
            FileNotFoundError: If input_file doesn't exist
            ConversionError: If conversion fails
        """
        # Validate format
        if not self.registry.has_format(output_format):
            available = self.registry.list_formats()
            raise InvalidFormatError(output_format, available)

        # Validate input file
        input_path = validate_file_exists(input_file)

        # Get converter
        converter_class = self.registry.get(output_format)
        converter = converter_class(self.pandoc_wrapper)

        # Prepare output
        if output_file:
            output_path = validate_output_directory(output_file)
            result = converter.convert(str(input_path), str(output_path), **options)
            return None
        else:
            return converter.convert(str(input_path), None, **options)

    def convert_string(
        self,
        markdown_content: str,
        output_format: str,
        output_file: Optional[Union[str, Path]] = None,
        **options,
    ) -> Optional[bytes]:
        """
        Convert markdown string to another format.

        Args:
            markdown_content: Markdown content as string
            output_format: Target format (e.g., 'html', 'pdf', 'docx')
            output_file: Optional output file path. If None, returns bytes.
            **options: Format-specific options

        Returns:
            Converted content as bytes if output_file is None, otherwise None

        Raises:
            InvalidFormatError: If output_format is not supported
            ConversionError: If conversion fails
        """
        # Validate format
        if not self.registry.has_format(output_format):
            available = self.registry.list_formats()
            raise InvalidFormatError(output_format, available)

        # Get converter
        converter_class = self.registry.get(output_format)
        converter = converter_class(self.pandoc_wrapper)

        # Convert
        if output_file:
            output_path = validate_output_directory(output_file)
            result = converter.convert(markdown_content, str(output_path), **options)
            return None
        else:
            return converter.convert(markdown_content, None, **options)

    def list_formats(self) -> List[str]:
        """List all supported output formats."""
        return self.registry.list_formats()

