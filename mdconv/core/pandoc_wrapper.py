"""Pandoc subprocess wrapper."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from mdconv.utils.exceptions import PandocNotFoundError, ConversionError


class PandocWrapper:
    """Wrapper around pandoc command-line tool."""

    def __init__(self, pandoc_path: Optional[str] = None):
        """
        Initialize the pandoc wrapper.

        Args:
            pandoc_path: Optional path to pandoc executable. If None, searches PATH.
        """
        self.pandoc_path = pandoc_path or self._find_pandoc()
        if not self.pandoc_path:
            raise PandocNotFoundError()

    @staticmethod
    def _find_pandoc() -> Optional[str]:
        """
        Find pandoc executable in PATH or pypandoc-binary installation.
        
        Checks:
        1. System PATH
        2. pypandoc-binary installation location (if available)
        """
        # First, check system PATH
        pandoc_path = shutil.which("pandoc")
        if pandoc_path:
            return pandoc_path
        
        # If not found, try to find pypandoc-binary installation
        try:
            import pypandoc
            # pypandoc-binary includes pandoc, use pypandoc's method to find it
            try:
                # Method 1: Use pypandoc's get_pandoc_path() function
                base_path = pypandoc.get_pandoc_path()
                if base_path:
                    # Check for executable with and without .exe extension
                    possible_paths = [
                        base_path,
                        base_path + ".exe",
                        os.path.join(base_path, "pandoc"),
                        os.path.join(base_path, "pandoc.exe"),
                    ]
                    for path in possible_paths:
                        if os.path.exists(path) and os.access(path, os.X_OK):
                            return path
            except (AttributeError, TypeError):
                pass
            
            # Method 2: Check __pandoc_path attribute
            try:
                if hasattr(pypandoc, "__pandoc_path") and pypandoc.__pandoc_path:
                    base_path = pypandoc.__pandoc_path
                    possible_paths = [
                        base_path,
                        base_path + ".exe",
                    ]
                    for path in possible_paths:
                        if os.path.exists(path) and os.access(path, os.X_OK):
                            return path
            except (AttributeError, TypeError):
                pass
            
            # Method 3: Search in pypandoc package directory
            pypandoc_dir = os.path.dirname(pypandoc.__file__)
            # Check common locations for pandoc binary in pypandoc-binary
            possible_paths = [
                os.path.join(pypandoc_dir, "files", "pandoc"),
                os.path.join(pypandoc_dir, "files", "pandoc.exe"),
                os.path.join(pypandoc_dir, "pandoc", "pandoc"),
                os.path.join(pypandoc_dir, "pandoc", "pandoc.exe"),
                os.path.join(pypandoc_dir, "pandoc.exe"),
            ]
            for path in possible_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    return path
        except ImportError:
            pass
        
        return None

    def check_available(self) -> bool:
        """Check if pandoc is available."""
        return self.pandoc_path is not None and Path(self.pandoc_path).exists()

    def convert(
        self,
        input_data: str,
        input_format: str,
        output_format: str,
        output_file: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> bytes:
        """
        Convert input data using pandoc.

        Args:
            input_data: Input content as string (for stdin) or file path
            input_format: Input format (e.g., 'markdown')
            output_format: Output format (e.g., 'html')
            output_file: Optional output file path. If None, returns bytes.
            options: Optional dictionary of pandoc options

        Returns:
            Converted content as bytes if output_file is None, otherwise empty bytes

        Raises:
            ConversionError: If conversion fails
        """
        options = options or {}
        cmd = [self.pandoc_path, f"--from={input_format}", f"--to={output_format}"]

        # Add options
        for key, value in options.items():
            if value is True:
                cmd.append(f"--{key}")
            elif value is False:
                continue
            elif isinstance(value, list):
                for item in value:
                    cmd.append(f"--{key}={item}")
            else:
                cmd.append(f"--{key}={value}")

        # Handle input
        # Check if input_data is a file path (not content)
        # Only treat as file if it's a short string (likely a path) and the file exists
        input_is_file = False
        if isinstance(input_data, str):
            # Only check if it looks like a path (short, no newlines, exists)
            # Long strings or strings with newlines are content, not file paths
            if len(input_data) < 260 and '\n' not in input_data:
                try:
                    input_is_file = Path(input_data).exists()
                except (OSError, ValueError):
                    # If path is invalid or too long, treat as content
                    input_is_file = False
        
        if input_is_file:
            cmd.append(input_data)
            stdin_data = None
        else:
            cmd.append("-")  # Read from stdin
            stdin_data = input_data.encode("utf-8") if isinstance(input_data, str) else input_data

        # Handle output
        # Some formats (docx, epub, pptx) require -o - to write to stdout
        formats_requiring_stdout_flag = {"docx", "epub", "pptx"}
        if output_file:
            cmd.extend(["-o", str(output_file)])
            stdout_target = subprocess.DEVNULL
        else:
            if output_format in formats_requiring_stdout_flag:
                cmd.extend(["-o", "-"])  # Force stdout output
            stdout_target = subprocess.PIPE

        try:
            result = subprocess.run(
                cmd,
                input=stdin_data,
                stdout=stdout_target,
                stderr=subprocess.PIPE,
                check=True,
            )
            return result.stdout if result.stdout else b""
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8") if e.stderr else "Unknown pandoc error"
            # Check if the error is about file name too long - this might be from the OS, not pandoc
            if "File name too long" in error_msg or "[Errno 36]" in error_msg:
                # This error might be from Python/OS, not pandoc stderr
                # Try to get more context
                import traceback
                full_error = f"Pandoc command: {' '.join(cmd)}\nPandoc stderr: {error_msg}\nPython error: {str(e)}"
                raise ConversionError(f"Pandoc conversion failed: {error_msg}", full_error)
            raise ConversionError(f"Pandoc conversion failed: {error_msg}", error_msg)
        except FileNotFoundError:
            raise PandocNotFoundError()

    def get_version(self) -> str:
        """Get pandoc version."""
        try:
            result = subprocess.run(
                [self.pandoc_path, "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.split("\n")[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "Unknown"

