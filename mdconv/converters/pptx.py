"""PPTX converter."""

import re
import tempfile
from pathlib import Path
from typing import Optional

from mdconv.converters.base import BaseConverter
from mdconv.utils.pptx_themes import get_theme


class PPTXConverter(BaseConverter):
    """Converter for PPTX (PowerPoint) output."""

    @property
    def format_name(self) -> str:
        """Return format name."""
        return "pptx"

    def convert(
        self,
        input_data: str,
        output_file: Optional[str] = None,
        **options,
    ) -> bytes:
        """
        Convert markdown to PPTX (PowerPoint presentation).

        Args:
            input_data: Input markdown content or file path
            output_file: Optional output file path
            **options: PPTX-specific options:
                - slide_level: Heading level that starts a new slide (default: auto-detect)
                    Level 1 = # headings start slides
                    Level 2 = ## headings start slides
                - toc: Include table of contents slide (default: False)
                - reference_doc: Reference PPTX template file for styling
                - theme: Predefined theme name ('modern', 'classic', 'minimal', 'dark', 'corporate')
                - theme_color: Primary theme color (hex code or color name)
                - background_color: Slide background color
                - heading_color: Heading text color
                - font_family: Font family name
                - font_size: Base font size
                - background_image: Default background image path for slides
        """
        # Handle theme presets
        if "theme" in options:
            try:
                theme_options = get_theme(options["theme"])
                # Merge theme options, but allow user options to override
                for key, value in theme_options.items():
                    if key not in options:
                        options[key] = value
            except KeyError as e:
                # If theme not found, continue without theme
                pass

        # Get content for processing
        # Only treat as file if it's a short string (likely a path) and the file exists
        is_file = False
        if isinstance(input_data, str):
            # Only check if it looks like a path (short, no newlines, exists)
            # Long strings or strings with newlines are content, not file paths
            if len(input_data) < 260 and '\n' not in input_data:
                try:
                    is_file = Path(input_data).exists()
                except (OSError, ValueError):
                    # If path is invalid or too long, treat as content
                    is_file = False
        
        if is_file:
            content = Path(input_data).read_text(encoding="utf-8")
            input_file_path = input_data
        else:
            content = input_data
            input_file_path = None

        # Auto-detect slide level if not explicitly set
        slide_level = options.get("slide_level")
        if slide_level is None:
            slide_level = self._detect_slide_level(content)
            options["slide_level"] = slide_level

        # Ensure proper slide breaks by normalizing structure
        content = self._normalize_slide_structure(content, slide_level)

        # Inject styling metadata into markdown
        input_with_metadata = self._inject_styling_metadata(content, options, is_file=False)

        pandoc_options = {}

        # Slide level (which heading level starts a new slide)
        pandoc_options["slide-level"] = slide_level

        # Reference document/template for styling
        if "reference_doc" in options:
            pandoc_options["reference-doc"] = options["reference_doc"]

        # Table of contents slide
        if options.get("toc", False):
            pandoc_options["toc"] = True
            pandoc_options["toc-depth"] = options.get("toc_depth", 3)

        # For PPTX, pandoc has issues with stdin input when processing markdown content
        # Always use a temporary file to avoid "File name too long" errors
        # Create a temporary file with the markdown content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(input_with_metadata)
            tmp_file_path = tmp_file.name
        
        try:
            # Use the temporary file as input
            result = self.pandoc_wrapper.convert(
                input_data=tmp_file_path,
                input_format="markdown",
                output_format="pptx",
                output_file=output_file,
                options=pandoc_options,
            )
        finally:
            # Clean up temporary file
            try:
                Path(tmp_file_path).unlink()
            except OSError:
                pass  # Ignore cleanup errors
        
        return result

    def _detect_slide_level(self, content: str) -> int:
        """
        Auto-detect the appropriate slide level based on heading structure.

        Args:
            content: Markdown content

        Returns:
            Detected slide level (1 or 2)
        """
        lines = content.split("\n")
        heading_levels = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                # Count leading # to determine heading level
                level = len(stripped) - len(stripped.lstrip("#"))
                if level > 0 and level <= 6:
                    heading_levels.append(level)
        
        if not heading_levels:
            return 1  # Default to level 1
        
        # Find the most common heading level (excluding the first heading if it's a title)
        # If we have multiple level 2+ headings, use level 2
        level_2_count = sum(1 for level in heading_levels if level == 2)
        level_1_count = sum(1 for level in heading_levels if level == 1)
        
        # If there are multiple level 2 headings and only one (or no) level 1 heading,
        # it's likely that level 2 should be the slide level
        if level_2_count > 1 and level_1_count <= 1:
            return 2
        
        # Otherwise, default to level 1
        return 1

    def _normalize_slide_structure(self, content: str, slide_level: int) -> str:
        """
        Normalize markdown structure to ensure proper slide breaks.

        Args:
            content: Markdown content
            slide_level: Heading level that starts slides

        Returns:
            Normalized markdown content
        """
        lines = content.split("\n")
        normalized_lines = []
        found_first_slide = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check if this is a heading at the slide level
            is_slide_heading = (
                stripped.startswith("#" * slide_level) and
                not stripped.startswith("#" * (slide_level + 1)) and
                len(stripped) > slide_level and
                stripped[slide_level] in (" ", "\t")
            )
            
            # If we find a slide-level heading (not the first one)
            if is_slide_heading and found_first_slide:
                # Ensure blank line before horizontal rule
                if normalized_lines and normalized_lines[-1].strip():
                    normalized_lines.append("")
                # Add horizontal rule to force slide break (Pandoc uses this)
                normalized_lines.append("---")
                normalized_lines.append("")
            elif is_slide_heading:
                found_first_slide = True
            
            normalized_lines.append(line)
        
        # Join lines
        result = "\n".join(normalized_lines)
        
        # Ensure proper spacing after slide headings (helps Pandoc)
        # Add blank line after slide-level headings if missing
        heading_pattern = "#" * slide_level + " "
        lines_result = result.split("\n")
        fixed_lines = []
        
        for i, line in enumerate(lines_result):
            fixed_lines.append(line)
            # If this is a slide-level heading and next line is not blank
            if (line.strip().startswith(heading_pattern) and 
                i + 1 < len(lines_result) and 
                lines_result[i + 1].strip() and
                not lines_result[i + 1].strip().startswith("---")):
                fixed_lines.append("")
        
        result = "\n".join(fixed_lines)
        
        # Clean up excessive blank lines (keep max 2 consecutive)
        result = re.sub(r"\n{3,}", "\n\n", result)
        
        return result

    def _inject_styling_metadata(
        self, input_data: str, options: dict, is_file: bool = True
    ) -> str:
        """
        Inject YAML metadata with styling options into markdown.

        Args:
            input_data: Input markdown content or file path
            options: Styling options dictionary
            is_file: Whether input_data is a file path (default: True)

        Returns:
            Markdown content with injected YAML metadata
        """
        # Check if input is a file path
        if is_file and Path(input_data).exists():
            content = Path(input_data).read_text(encoding="utf-8")
        else:
            content = input_data

        # Build YAML metadata block
        metadata_lines = []

        # Styling options that can be passed via YAML metadata
        styling_options = {
            "theme_color": "theme-color",
            "background_color": "background-color",
            "heading_color": "heading-color",
            "font_family": "font-family",
            "font_size": "font-size",
            "background_image": "background-image",
        }

        for option_key, yaml_key in styling_options.items():
            if option_key in options:
                metadata_lines.append(f"{yaml_key}: {options[option_key]}")

        # If no styling metadata to add, return original content
        if not metadata_lines:
            return content

        # Check if YAML frontmatter already exists
        if content.strip().startswith("---"):
            # Find the end of existing YAML block
            lines = content.split("\n")
            yaml_end_idx = None
            for i, line in enumerate(lines[1:], start=1):
                if line.strip() == "---":
                    yaml_end_idx = i
                    break

            if yaml_end_idx is not None:
                # Merge with existing metadata
                existing_yaml = "\n".join(lines[1:yaml_end_idx])
                new_yaml = "\n".join(metadata_lines)
                # Combine existing and new metadata
                combined_yaml = f"{existing_yaml}\n{new_yaml}" if existing_yaml.strip() else new_yaml
                return f"---\n{combined_yaml}\n---\n" + "\n".join(lines[yaml_end_idx + 1:])

        # Prepend new metadata block
        metadata_block = "---\n" + "\n".join(metadata_lines) + "\n---\n"
        return metadata_block + content

