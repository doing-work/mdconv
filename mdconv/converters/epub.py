"""EPUB converter."""

from typing import Optional

from mdconv.converters.base import BaseConverter


class EPUBConverter(BaseConverter):
    """Converter for EPUB output."""

    @property
    def format_name(self) -> str:
        """Return format name."""
        return "epub"

    def convert(
        self,
        input_data: str,
        output_file: Optional[str] = None,
        **options,
    ) -> bytes:
        """
        Convert markdown to EPUB.

        Args:
            input_data: Input markdown content or file path
            output_file: Optional output file path
            **options: EPUB-specific options:
                - toc: Include table of contents (default: True for EPUB)
                - toc_depth: Depth of TOC (default: 3)
                - epub_cover_image: Cover image path
                - epub_metadata: Metadata file path
        """
        pandoc_options = {}

        # Table of contents (default True for EPUB)
        if options.get("toc", True):
            pandoc_options["toc"] = True
            pandoc_options["toc-depth"] = options.get("toc_depth", 3)

        # Cover image
        if "epub_cover_image" in options:
            pandoc_options["epub-cover-image"] = options["epub_cover_image"]

        # Metadata
        if "epub_metadata" in options:
            pandoc_options["epub-metadata"] = options["epub_metadata"]

        return self.pandoc_wrapper.convert(
            input_data=input_data,
            input_format="markdown",
            output_format="epub",
            output_file=output_file,
            options=pandoc_options,
        )

