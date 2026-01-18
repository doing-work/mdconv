
# mdconv

**mdconv** is a lightweight, modular Python package that wraps **Pandoc** to convert Markdown into multiple output formats. It is designed for simplicity, extensibility, and easy integration into other projects.

---

## ✨ Features

* **Modular Architecture**
  Each format converter is independent and easily extensible.

* **Simple API**
  Clean, intuitive interface for both library and CLI usage.

* **Multiple Formats**
  Supports HTML, PDF, DOCX, LaTeX, EPUB, and PPTX.

* **Format-Specific Options**
  Tailored conversion options for each output format.

* **Easy Integration**
  Designed to plug seamlessly into existing projects and web apps.

---

## 📦 Installation

### Install with pip (recommended)

```bash
pip install -e .
```

### Install from source

```bash
git clone <repository-url>
cd mdconv
pip install -e .
```

> **Note**
> `pypandoc-binary` (included in `requirements.txt`) bundles Pandoc, so no separate installation is required.
> If you prefer a manual Pandoc installation, download it from
> [https://pandoc.org/installing.html](https://pandoc.org/installing.html) and remove `pypandoc-binary` from `requirements.txt`.

---

## 🚀 Usage

### Library API

#### Basic Conversion

```python
from mdconv import Converter

converter = Converter()

# File → file
converter.convert("input.md", "html", "output.html")

# String → string
html = converter.convert_string("# Hello World", "html")
print(html.decode("utf-8"))
```

---

### Format-Specific Options

#### HTML

```python
converter.convert(
    "input.md",
    "html",
    "output.html",
    standalone=True,     # Generate standalone HTML
    toc=True,            # Include table of contents
    css=["style.css"],   # Include CSS files
    mathjax=True         # Enable MathJax
)
```

#### PDF

```python
converter.convert(
    "input.md",
    "pdf",
    "output.pdf",
    pdf_engine="wkhtmltopdf",  # PDF engine
    toc=True,                  # Table of contents
    geometry="margin=1in",     # Page geometry
    fontsize="12pt"            # Font size
)
```

#### DOCX

```python
converter.convert(
    "input.md",
    "docx",
    "output.docx",
    reference_doc="template.docx",  # Styling reference document
    toc=True
)
```

#### LaTeX

```python
converter.convert(
    "input.md",
    "latex",
    "output.tex",
    standalone=True,
    documentclass="article",
    geometry="margin=1in",
    toc=True
)
```

#### EPUB

```python
converter.convert(
    "input.md",
    "epub",
    "output.epub",
    toc=True,
    epub_cover_image="cover.jpg",
    epub_metadata="metadata.xml"
)
```

#### PPTX

```python
converter.convert(
    "presentation.md",
    "pptx",
    "presentation.pptx",
    slide_level=1,                  # Heading level that starts slides
    toc=True,                       # Include TOC slide
    reference_doc="template.pptx",  # Reference PPTX
    theme="modern",                 # modern | classic | minimal | dark | corporate
    theme_color="#3498db",
    background_color="#ffffff",
    heading_color="#2c3e50",
    font_family="Arial",
    font_size=18,
    background_image="bg.jpg"
)
```

---

### List Supported Formats

```python
formats = converter.list_formats()
print(formats)
# ['docx', 'epub', 'html', 'latex', 'pdf', 'pptx']
```

---

## 🖥️ Command-Line Interface

### Basic Usage

```bash
# Markdown → HTML
mdconv input.md -f html -o output.html

# Markdown → PDF
mdconv input.md -f pdf -o output.pdf

# Auto-generate output filename
mdconv input.md -f html
```

---

### CLI Options Examples

```bash
# HTML with TOC and standalone document
mdconv input.md -f html --standalone --toc

# PDF with custom engine
mdconv input.md -f pdf --pdf-engine=wkhtmltopdf --geometry="margin=1in"

# DOCX with reference document
mdconv input.md -f docx --reference-doc=template.docx --toc

# EPUB with cover image
mdconv input.md -f epub --epub-cover-image=cover.jpg
```

#### PPTX Examples

```bash
# Default PPTX
mdconv presentation.md -f pptx

# Slides start at ##
mdconv presentation.md -f pptx --slide-level=2

# With TOC slide
mdconv presentation.md -f pptx --toc

# Predefined theme
mdconv presentation.md -f pptx --pptx-theme=modern

# Custom styling
mdconv presentation.md -f pptx \
  --pptx-theme-color="#3498db" \
  --pptx-bg-color="#ffffff" \
  --pptx-heading-color="#2c3e50" \
  --pptx-font="Arial" \
  --pptx-font-size=18

# Background image
mdconv presentation.md -f pptx \
  --pptx-bg-image=background.jpg \
  --pptx-theme=dark
```

---

### List Available Formats

```bash
mdconv --list-formats
```

---

## 📄 Supported Formats

* **HTML** — HTML5 output
* **PDF** — via pdflatex, xelatex, lualatex, wkhtmltopdf, weasyprint, prince, context, pdfroff, xhtml2pdf
* **DOCX** — Microsoft Word
* **LaTeX** — LaTeX source
* **EPUB** — EPUB e-books
* **PPTX** — PowerPoint presentations

---

## 🏗️ Architecture

```
mdconv/
├── core/        # Core conversion engine
├── converters/  # Modular, format-specific converters
├── cli/         # Command-line interface
└── utils/       # Shared utilities
```

Each converter is independent. New formats can be added without affecting existing ones.

---

## 🔧 Extending mdconv

### Step 1: Create a converter

```python
from mdconv.converters.base import BaseConverter

class MyFormatConverter(BaseConverter):
    @property
    def format_name(self) -> str:
        return "myformat"

    def convert(self, input_data: str, output_file=None, **options):
        pass
```

### Step 2: Register the converter

```python
from mdconv.converters.myformat import MyFormatConverter

registry.register("myformat", MyFormatConverter)
```

---

## ⚠️ Error Handling

mdconv provides clear, typed exceptions:

* `PandocNotFoundError`
* `InvalidFormatError`
* `ConversionError`

---

## 📋 Requirements

* Python 3.7+
* Pandoc (bundled via `pypandoc-binary` or installed manually)

---

## 📜 License

*Specify your license here.*

---

## 🌐 Web API Integration

mdconv integrates easily with web apps (React, Vue, etc.) using a REST API.

### Local Development

1. **Install API dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Start the API server**

   ```bash
   python api_server.py
   ```

3. **Use from React**

   ```javascript
   const response = await fetch("http://localhost:8000/convert", {
     method: "POST",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify({
       content: "# Hello World",
       output_format: "html",
       options: { standalone: true },
     }),
   });

   const blob = await response.blob();
   ```

See `examples/react/` for integration examples.

---

## 🤝 Contributing

Contributions are welcome!
Please feel free to submit a Pull Request.
