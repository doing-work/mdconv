"""LaTeX converter."""

from typing import Optional

from mdconv.converters.base import BaseConverter


class LaTeXConverter(BaseConverter):
    """Converter for LaTeX output."""

    @property
    def format_name(self) -> str:
        """Return format name."""
        return "latex"

    def convert(
        self,
        input_data: str,
        output_file: Optional[str] = None,
        **options,
    ) -> bytes:
        """
        Convert markdown to LaTeX.

        Args:
            input_data: Input markdown content or file path
            output_file: Optional output file path
            **options: LaTeX-specific options:
                - standalone: Generate standalone document (default: False)
                - toc: Include table of contents (default: False)
                - documentclass: Document class (default: 'article')
                - geometry: Page geometry (e.g., 'margin=1in')
        """
        pandoc_options = {}

        # Standalone document
        if options.get("standalone", False):
            pandoc_options["standalone"] = True

        # Document class
        if "documentclass" in options:
            pandoc_options["variable"] = f"documentclass:{options['documentclass']}"
        else:
            pandoc_options["variable"] = "documentclass:article"

        # Table of contents
        if options.get("toc", False):
            pandoc_options["toc"] = True
            pandoc_options["toc-depth"] = options.get("toc_depth", 3)

        # Geometry
        if "geometry" in options:
            pandoc_options["geometry"] = options["geometry"]

        return self.pandoc_wrapper.convert(
            input_data=input_data,
            input_format="markdown",
            output_format="latex",
            output_file=output_file,
            options=pandoc_options,
        )

