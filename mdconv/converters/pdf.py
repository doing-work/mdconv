"""PDF converter."""

from typing import Optional

from mdconv.converters.base import BaseConverter
from mdconv.utils.exceptions import ConversionError


class PDFConverter(BaseConverter):
    """Converter for PDF output."""

    @property
    def format_name(self) -> str:
        """Return format name."""
        return "pdf"

    def convert(
        self,
        input_data: str,
        output_file: Optional[str] = None,
        **options,
    ) -> bytes:
        """
        Convert markdown to PDF.

        Args:
            input_data: Input markdown content or file path
            output_file: Optional output file path
            **options: PDF-specific options:
                - pdf_engine: PDF engine to use ('pdflatex', 'xelatex', 'lualatex', 'wkhtmltopdf', 'weasyprint', 'prince', 'context', 'pdfroff', 'xhtml2pdf')
                  Use 'xhtml2pdf' for pure Python, FOSS solution with no system dependencies
                - toc: Include table of contents (default: False)
                - toc_depth: Depth of TOC (default: 3)
                - highlight_style: Code highlighting style
                - geometry: Page geometry (e.g., 'margin=1in')
                - fontsize: Font size (e.g., '12pt')
        """
        # Check if using pure Python engine (default to xhtml2pdf - no dependencies)
        pdf_engine = options.get("pdf_engine", "xhtml2pdf")
        if pdf_engine == "xhtml2pdf":
            # Use pure Python converter
            from mdconv.converters.pdf_pure import PurePDFConverter
            pure_converter = PurePDFConverter(self.pandoc_wrapper)
            return pure_converter.convert(input_data, output_file, **options)

        # Use pandoc's PDF engines
        pandoc_options = {}
        pandoc_options["pdf-engine"] = pdf_engine

        # Table of contents
        if options.get("toc", False):
            pandoc_options["toc"] = True
            pandoc_options["toc-depth"] = options.get("toc_depth", 3)

        # Highlight style
        if "highlight_style" in options:
            pandoc_options["highlight-style"] = options["highlight_style"]

        # Geometry
        if "geometry" in options:
            pandoc_options["geometry"] = options["geometry"]

        # Font size
        if "fontsize" in options:
            pandoc_options["variable"] = f"fontsize:{options['fontsize']}"

        return self.pandoc_wrapper.convert(
            input_data=input_data,
            input_format="markdown",
            output_format="pdf",
            output_file=output_file,
            options=pandoc_options,
        )

