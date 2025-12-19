"""PPTX theme definitions."""

PPTX_THEMES = {
    "modern": {
        "theme_color": "#3498db",
        "background_color": "#ffffff",
        "heading_color": "#2c3e50",
        "font_family": "Arial",
        "font_size": 18,
    },
    "classic": {
        "theme_color": "#1a1a1a",
        "background_color": "#ffffff",
        "heading_color": "#000000",
        "font_family": "Times New Roman",
        "font_size": 16,
    },
    "minimal": {
        "theme_color": "#333333",
        "background_color": "#f8f8f8",
        "heading_color": "#222222",
        "font_family": "Helvetica",
        "font_size": 20,
    },
    "dark": {
        "theme_color": "#e74c3c",
        "background_color": "#2c3e50",
        "heading_color": "#ecf0f1",
        "font_family": "Arial",
        "font_size": 18,
    },
    "corporate": {
        "theme_color": "#0066cc",
        "background_color": "#ffffff",
        "heading_color": "#003366",
        "font_family": "Calibri",
        "font_size": 18,
    },
}


def get_theme(theme_name: str) -> dict:
    """
    Get theme configuration by name.

    Args:
        theme_name: Name of the theme

    Returns:
        Dictionary with theme configuration

    Raises:
        KeyError: If theme name is not found
    """
    if theme_name not in PPTX_THEMES:
        available = ", ".join(PPTX_THEMES.keys())
        raise KeyError(
            f"Theme '{theme_name}' not found. Available themes: {available}"
        )
    return PPTX_THEMES[theme_name].copy()

