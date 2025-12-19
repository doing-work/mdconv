"""Input validation utilities."""

import os
from pathlib import Path
from typing import Union


def validate_file_exists(file_path: Union[str, Path]) -> Path:
    """Validate that a file exists and return Path object."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    return path


def validate_output_directory(output_path: Union[str, Path]) -> Path:
    """Validate and create output directory if needed."""
    path = Path(output_path)
    parent = path.parent
    if parent and not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)
    return path

