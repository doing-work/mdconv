"""Format-specific converters."""

from mdconv.converters.base import BaseConverter, ConverterRegistry
from mdconv.converters.html import HTMLConverter
from mdconv.converters.pdf import PDFConverter
from mdconv.converters.docx import DOCXConverter
from mdconv.converters.latex import LaTeXConverter
from mdconv.converters.epub import EPUBConverter
from mdconv.converters.pptx import PPTXConverter

# Register all converters
registry = ConverterRegistry()
registry.register("html", HTMLConverter)
registry.register("pdf", PDFConverter)
registry.register("docx", DOCXConverter)
registry.register("latex", LaTeXConverter)
registry.register("epub", EPUBConverter)
registry.register("pptx", PPTXConverter)

__all__ = [
    "BaseConverter",
    "ConverterRegistry",
    "HTMLConverter",
    "PDFConverter",
    "DOCXConverter",
    "LaTeXConverter",
    "EPUBConverter",
    "PPTXConverter",
    "registry",
]

