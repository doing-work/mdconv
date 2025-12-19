"""DOCX converter."""

from typing import Optional

from mdconv.converters.base import BaseConverter


class DOCXConverter(BaseConverter):
    """Converter for DOCX (Word) output."""

    @property
    def format_name(self) -> str:
        """Return format name."""
        return "docx"

    def convert(
        self,
        input_data: str,
        output_file: Optional[str] = None,
        **options,
    ) -> bytes:
        """
        Convert markdown to DOCX.

        Args:
            input_data: Input markdown content or file path
            output_file: Optional output file path
            **options: DOCX-specific options:
                - reference_doc: Reference DOCX file for styling
                - toc: Include table of contents (default: False)
        """
        pandoc_options = {}

        # Reference document for styling
        if "reference_doc" in options:
            pandoc_options["reference-doc"] = options["reference_doc"]

        # Table of contents
        if options.get("toc", False):
            pandoc_options["toc"] = True
            pandoc_options["toc-depth"] = options.get("toc_depth", 3)

        return self.pandoc_wrapper.convert(
            input_data=input_data,
            input_format="markdown",
            output_format="docx",
            output_file=output_file,
            options=pandoc_options,
        )

