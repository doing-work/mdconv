"""Pure Python PDF converter using xhtml2pdf (no system dependencies)."""

from io import BytesIO
from pathlib import Path
from typing import Optional

from mdconv.converters.base import BaseConverter
from mdconv.utils.exceptions import ConversionError


class PurePDFConverter(BaseConverter):
    """Pure Python PDF converter using xhtml2pdf (FOSS, no system dependencies)."""

    @property
    def format_name(self) -> str:
        """Return format name."""
        return "pdf_pure"

    def convert(
        self,
        input_data: str,
        output_file: Optional[str] = None,
        **options,
    ) -> bytes:
        """
        Convert markdown to PDF using pure Python (xhtml2pdf).

        Args:
            input_data: Input markdown content or file path
            output_file: Optional output file path
            **options: PDF-specific options:
                - toc: Include table of contents (default: False)
                - toc_depth: Depth of TOC (default: 3)
                - standalone: Generate standalone HTML (default: True)
        """
        try:
            from xhtml2pdf import pisa
        except ImportError:
            raise ConversionError(
                "xhtml2pdf is not installed. Install it with: pip install xhtml2pdf"
            )

        # First, convert markdown to HTML using pandoc
        pandoc_options = {}
        
        # Table of contents
        if options.get("toc", False):
            pandoc_options["toc"] = True
            pandoc_options["toc-depth"] = options.get("toc_depth", 3)
        
        # Don't use standalone HTML - xhtml2pdf has trouble with pandoc's CSS
        # We'll add our own minimal CSS instead
        standalone = options.get("standalone", False)  # Default to False for xhtml2pdf
        if standalone:
            pandoc_options["standalone"] = True

        # Convert markdown to HTML
        html_content = self.pandoc_wrapper.convert(
            input_data=input_data,
            input_format="markdown",
            output_format="html",
            output_file=None,
            options=pandoc_options,
        )

        if not html_content:
            raise ConversionError("Failed to convert markdown to HTML")

        html_str = html_content.decode("utf-8")

        # Clean HTML/CSS for xhtml2pdf compatibility
        # xhtml2pdf doesn't support all CSS features (like :not(), :hover, etc.)
        html_str = self._clean_html_for_xhtml2pdf(html_str)

        # Convert HTML to PDF using xhtml2pdf
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as pdf_file:
                result = pisa.CreatePDF(
                    html_str,
                    dest=pdf_file,
                )
            
            if result.err:
                raise ConversionError(f"xhtml2pdf conversion failed: {result.err}")
            
            return b""
        else:
            # Return PDF as bytes - use BytesIO
            from io import BytesIO
            pdf_buffer = BytesIO()
            result = pisa.CreatePDF(
                html_str,
                dest=pdf_buffer,
            )
            
            if result.err:
                raise ConversionError(f"xhtml2pdf conversion failed: {result.err}")
            
            return pdf_buffer.getvalue()

    def _clean_html_for_xhtml2pdf(self, html: str) -> str:
        """
        Clean HTML/CSS to be compatible with xhtml2pdf.
        
        xhtml2pdf has very limited CSS support. This method removes
        all style tags and adds minimal, compatible CSS.
        """
        import re
        
        # Remove all style tags (pandoc's CSS is too complex for xhtml2pdf)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Add minimal CSS that xhtml2pdf can handle
        # Find the head tag or body tag to insert styles
        head_match = re.search(r'</head>', html, re.IGNORECASE)
        if head_match:
            # Insert before closing head tag
            minimal_css = """
    <style>
        body {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12pt;
            line-height: 1.4;
            margin: 1in;
        }
        h1 {
            font-size: 24pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        h2 {
            font-size: 20pt;
            font-weight: bold;
            margin-top: 0.8em;
            margin-bottom: 0.4em;
        }
        h3 {
            font-size: 16pt;
            font-weight: bold;
            margin-top: 0.6em;
            margin-bottom: 0.3em;
        }
        p {
            margin: 0.5em 0;
        }
        ul, ol {
            margin: 0.5em 0;
            padding-left: 2em;
        }
        li {
            margin: 0.2em 0;
        }
        code {
            font-family: "Courier New", monospace;
            font-size: 10pt;
        }
        pre {
            font-family: "Courier New", monospace;
            font-size: 10pt;
            margin: 1em 0;
            padding: 0.5em;
            border: 1px solid #ccc;
        }
        table {
            border-collapse: collapse;
            margin: 1em 0;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 0.3em 0.5em;
        }
        th {
            font-weight: bold;
            background-color: #f0f0f0;
        }
    </style>
"""
            html = html[:head_match.start()] + minimal_css + html[head_match.start():]
        else:
            # No head tag, insert before body
            body_match = re.search(r'<body[^>]*>', html, re.IGNORECASE)
            if body_match:
                html = html[:body_match.end()] + minimal_css + html[body_match.end():]
        
        return html

