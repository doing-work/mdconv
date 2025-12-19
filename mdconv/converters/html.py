"""HTML converter."""

from typing import Optional

from mdconv.converters.base import BaseConverter


class HTMLConverter(BaseConverter):
    """Converter for HTML output."""

    @property
    def format_name(self) -> str:
        """Return format name."""
        return "html"

    def convert(
        self,
        input_data: str,
        output_file: Optional[str] = None,
        **options,
    ) -> bytes:
        """
        Convert markdown to HTML.

        Args:
            input_data: Input markdown content or file path
            output_file: Optional output file path
            **options: HTML-specific options:
                - standalone: Generate standalone HTML (default: False)
                - toc: Include table of contents (default: False)
                - css: CSS file path(s) to include
                - template: Custom HTML template path
                - mathjax: Include MathJax for math rendering
        """
        pandoc_options = {}

        # Handle standalone HTML
        if options.get("standalone", False):
            pandoc_options["standalone"] = True

        # Handle table of contents
        if options.get("toc", False):
            pandoc_options["toc"] = True
            pandoc_options["toc-depth"] = options.get("toc_depth", 3)

        # Handle CSS files
        if "css" in options:
            css_files = options["css"]
            if isinstance(css_files, str):
                css_files = [css_files]
            pandoc_options["css"] = css_files

        # Handle template
        if "template" in options:
            pandoc_options["template"] = options["template"]

        # Handle MathJax
        if options.get("mathjax", False):
            pandoc_options["mathjax"] = True

        return self.pandoc_wrapper.convert(
            input_data=input_data,
            input_format="markdown",
            output_format="html",
            output_file=output_file,
            options=pandoc_options,
        )

