"""CLI command handlers."""

import argparse
import sys
from pathlib import Path

from mdconv import Converter
from mdconv.utils.exceptions import MDConvError


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert markdown files to various formats using pandoc",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input",
        type=str,
        help="Input markdown file path",
    )

    parser.add_argument(
        "-f",
        "--format",
        "--to",
        dest="output_format",
        required=True,
        help="Output format (html, pdf, docx, latex, epub, pptx)",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        type=str,
        help="Output file path (default: input filename with new extension)",
    )

    # Common options
    parser.add_argument(
        "--toc",
        action="store_true",
        help="Include table of contents",
    )

    parser.add_argument(
        "--toc-depth",
        type=int,
        default=3,
        help="Depth of table of contents (default: 3)",
    )

    # HTML-specific options
    parser.add_argument(
        "--standalone",
        action="store_true",
        help="Generate standalone HTML document",
    )

    parser.add_argument(
        "--css",
        action="append",
        help="CSS file(s) to include (can be used multiple times)",
    )

    parser.add_argument(
        "--mathjax",
        action="store_true",
        help="Include MathJax for math rendering",
    )

    # PDF-specific options
    parser.add_argument(
        "--pdf-engine",
        dest="pdf_engine",
        choices=["pdflatex", "xelatex", "lualatex", "wkhtmltopdf", "weasyprint", "prince", "context", "pdfroff", "xhtml2pdf"],
        default="xhtml2pdf",
        help="PDF engine to use (default: xhtml2pdf - pure Python, no dependencies)",
    )

    parser.add_argument(
        "--highlight-style",
        help="Code highlighting style",
    )

    parser.add_argument(
        "--geometry",
        help="Page geometry (e.g., 'margin=1in')",
    )

    parser.add_argument(
        "--fontsize",
        help="Font size (e.g., '12pt')",
    )

    # DOCX-specific options
    parser.add_argument(
        "--reference-doc",
        dest="reference_doc",
        help="Reference DOCX file for styling",
    )

    # EPUB-specific options
    parser.add_argument(
        "--epub-cover-image",
        dest="epub_cover_image",
        help="EPUB cover image path",
    )

    parser.add_argument(
        "--epub-metadata",
        dest="epub_metadata",
        help="EPUB metadata file path",
    )

    # PPTX-specific options
    parser.add_argument(
        "--slide-level",
        dest="slide_level",
        type=int,
        help="Heading level that starts a new slide (1=#, 2=##, default: 1)",
    )

    parser.add_argument(
        "--reference-pptx",
        dest="reference_pptx",
        help="Reference PPTX template file for styling",
    )

    parser.add_argument(
        "--pptx-theme",
        dest="pptx_theme",
        choices=["modern", "classic", "minimal", "dark", "corporate"],
        help="Predefined PPTX theme",
    )

    parser.add_argument(
        "--pptx-theme-color",
        dest="pptx_theme_color",
        help="Primary theme color (hex code or color name)",
    )

    parser.add_argument(
        "--pptx-bg-color",
        dest="pptx_background_color",
        help="Slide background color",
    )

    parser.add_argument(
        "--pptx-heading-color",
        dest="pptx_heading_color",
        help="Heading text color",
    )

    parser.add_argument(
        "--pptx-font",
        dest="pptx_font_family",
        help="Font family name",
    )

    parser.add_argument(
        "--pptx-font-size",
        dest="pptx_font_size",
        help="Base font size",
    )

    parser.add_argument(
        "--pptx-bg-image",
        dest="pptx_background_image",
        help="Default background image for slides",
    )

    # Utility options
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List all supported output formats and exit",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="mdconv 0.1.0",
    )

    args = parser.parse_args()

    # Handle list-formats
    if args.list_formats:
        converter = Converter()
        formats = converter.list_formats()
        print("Supported formats:")
        for fmt in formats:
            print(f"  - {fmt}")
        return 0

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Determine output file
    if args.output_file:
        output_file = Path(args.output_file)
    else:
        # Generate output filename from input
        output_file = input_path.with_suffix(f".{args.output_format}")

    # Build options dictionary
    options = {}

    # Common options
    if args.toc:
        options["toc"] = True
        options["toc_depth"] = args.toc_depth

    # HTML options
    if args.standalone:
        options["standalone"] = True
    if args.css:
        options["css"] = args.css
    if args.mathjax:
        options["mathjax"] = True

    # PDF options
    if args.pdf_engine:
        options["pdf_engine"] = args.pdf_engine
    if args.highlight_style:
        options["highlight_style"] = args.highlight_style
    if args.geometry:
        options["geometry"] = args.geometry
    if args.fontsize:
        options["fontsize"] = args.fontsize

    # DOCX options
    if args.reference_doc:
        options["reference_doc"] = args.reference_doc

    # EPUB options
    if args.epub_cover_image:
        options["epub_cover_image"] = args.epub_cover_image
    if args.epub_metadata:
        options["epub_metadata"] = args.epub_metadata

    # PPTX options
    if args.slide_level:
        options["slide_level"] = args.slide_level
    if args.reference_pptx:
        options["reference_doc"] = args.reference_pptx
    if args.pptx_theme:
        options["theme"] = args.pptx_theme
    if args.pptx_theme_color:
        options["theme_color"] = args.pptx_theme_color
    if args.pptx_background_color:
        options["background_color"] = args.pptx_background_color
    if args.pptx_heading_color:
        options["heading_color"] = args.pptx_heading_color
    if args.pptx_font_family:
        options["font_family"] = args.pptx_font_family
    if args.pptx_font_size:
        options["font_size"] = args.pptx_font_size
    if args.pptx_background_image:
        options["background_image"] = args.pptx_background_image

    # Perform conversion
    try:
        converter = Converter()
        converter.convert(
            input_file=str(input_path),
            output_format=args.output_format,
            output_file=str(output_file),
            **options,
        )
        print(f"Successfully converted to: {output_file}")
        return 0
    except MDConvError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

