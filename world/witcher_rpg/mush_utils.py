"""
MUSH text processing utilities for the Witcher RPG.

Provides functions to handle MUSH-style formatting tokens like %r, %t, %b,
and color codes for both in-game and web display.
"""

import re


def convert_mush_tokens(text):
    """
    Convert MUSH-style tokens to Evennia-compatible formatting.

    Token conversions:
        %r  - Carriage return (newline)
        %t  - Tab (4 spaces)
        %b  - Space
        %cr - Red color
        %cg - Green color
        %cy - Yellow color
        %cb - Blue color
        %cm - Magenta color
        %cc - Cyan color
        %cw - White color
        %cn - Reset color
        %ch - Highlight
        %cx - Black color

    Args:
        text (str): Text with MUSH tokens

    Returns:
        str: Text with Evennia formatting codes
    """
    conversions = {
        '%r': '\n',    # Carriage return
        '%R': '\n',    # Carriage return (uppercase variant)
        '%t': '    ',  # Tab (4 spaces)
        '%T': '    ',  # Tab (uppercase variant)
        '%b': ' ',     # Space
        '%B': ' ',     # Space (uppercase variant)
        '%cr': '|r',   # Red color
        '%cR': '|r',   # Red color (uppercase)
        '%cg': '|g',   # Green color
        '%cG': '|g',   # Green color (uppercase)
        '%cy': '|y',   # Yellow color
        '%cY': '|y',   # Yellow color (uppercase)
        '%cb': '|b',   # Blue color
        '%cB': '|b',   # Blue color (uppercase)
        '%cm': '|m',   # Magenta color
        '%cM': '|m',   # Magenta color (uppercase)
        '%cc': '|c',   # Cyan color
        '%cC': '|c',   # Cyan color (uppercase)
        '%cw': '|w',   # White color
        '%cW': '|w',   # White color (uppercase)
        '%cn': '|n',   # Reset color
        '%cN': '|n',   # Reset color (uppercase)
        '%ch': '|h',   # Highlight
        '%cH': '|h',   # Highlight (uppercase)
        '%cx': '|x',   # Black color
        '%cX': '|x',   # Black color (uppercase)
    }

    for token, replacement in conversions.items():
        text = text.replace(token, replacement)

    return text


def process_ansi_codes(text):
    """
    Process ANSI-style codes like %xr and %xt.

    This is for compatibility with some MUSH codebases that use
    %xr for newline and %xt for tab.

    Args:
        text (str): Text with ANSI codes

    Returns:
        str: Text with processed codes
    """
    # Replace %xr with newline and %xt with tab
    text = re.sub(r'%xr', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'%xt', '\t', text, flags=re.IGNORECASE)
    return text


def process_mush_text(text, for_web=False):
    """
    Process MUSH text for either in-game or web display.

    Args:
        text (str): Text with MUSH formatting
        for_web (bool): If True, convert to HTML format; if False, convert to Evennia format

    Returns:
        str: Processed text
    """
    if for_web:
        # For web display, convert %r to <br> and preserve tabs
        text = text.replace('%r', '<br>')
        text = text.replace('%R', '<br>')
        text = text.replace('%t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        text = text.replace('%T', '&nbsp;&nbsp;&nbsp;&nbsp;')
        text = text.replace('%b', '&nbsp;')
        text = text.replace('%B', '&nbsp;')

        # Convert color codes to HTML spans
        color_map = {
            '%cr': '<span style="color: #ff0000;">',
            '%cg': '<span style="color: #00ff00;">',
            '%cy': '<span style="color: #ffff00;">',
            '%cb': '<span style="color: #0000ff;">',
            '%cm': '<span style="color: #ff00ff;">',
            '%cc': '<span style="color: #00ffff;">',
            '%cw': '<span style="color: #ffffff;">',
            '%cn': '</span>',
            '%ch': '<strong>',
            '%cx': '<span style="color: #000000;">',
        }

        # Process uppercase variants too
        for token in list(color_map.keys()):
            upper_token = token[0] + token[1].upper() + (token[2].upper() if len(token) > 2 else '')
            color_map[upper_token] = color_map[token]

        for token, html in color_map.items():
            text = text.replace(token, html)

        return text
    else:
        # For in-game display, convert to Evennia formatting
        return convert_mush_tokens(text)


def format_table_row(*columns, widths=None, separator=' ', align='left'):
    """
    Format a table row with proper column widths (MUSH-style).

    Args:
        *columns: Column values to display
        widths (list): List of column widths (optional)
        separator (str): Column separator (default: single space)
        align (str): Text alignment ('left', 'right', 'center')

    Returns:
        str: Formatted table row
    """
    if not widths:
        widths = [20] * len(columns)

    parts = []
    for col, width in zip(columns, widths):
        col_str = str(col)
        if align == 'left':
            parts.append(col_str.ljust(width))
        elif align == 'right':
            parts.append(col_str.rjust(width))
        elif align == 'center':
            parts.append(col_str.center(width))
        else:
            parts.append(col_str.ljust(width))

    return separator.join(parts)


def format_header(title, width=70, fill_char='='):
    """
    Format a MUSH-style header.

    Args:
        title (str): Header title
        width (int): Total width of header
        fill_char (str): Character to use for filling (default: '=')

    Returns:
        str: Formatted header with newlines
    """
    lines = []
    lines.append(fill_char * width)
    if title:
        lines.append(title)
    lines.append(fill_char * width)
    return '%r'.join(lines)


def format_footer(width=70, fill_char='='):
    """
    Format a MUSH-style footer.

    Args:
        width (int): Total width of footer
        fill_char (str): Character to use for filling (default: '=')

    Returns:
        str: Formatted footer
    """
    return fill_char * width


def format_section_header(title, width=70):
    """
    Format a section header within a larger output.

    Args:
        title (str): Section title
        width (int): Total width

    Returns:
        str: Formatted section header
    """
    return title


def wrap_output(*lines):
    """
    Wrap multiple lines with proper MUSH formatting.

    Args:
        *lines: Lines to join

    Returns:
        str: Lines joined with %r tokens
    """
    return '%r'.join(str(line) for line in lines)


def mush_table(headers, rows, widths=None, separator=' '):
    """
    Create a complete MUSH-style table.

    Args:
        headers (list): Column headers
        rows (list): List of row tuples/lists
        widths (list): Column widths (optional)
        separator (str): Column separator

    Returns:
        str: Complete formatted table
    """
    if not widths:
        widths = [15] * len(headers)

    lines = []

    # Header row
    lines.append(format_table_row(*headers, widths=widths, separator=separator))

    # Separator line
    sep_parts = ['-' * w for w in widths]
    lines.append(separator.join(sep_parts))

    # Data rows
    for row in rows:
        lines.append(format_table_row(*row, widths=widths, separator=separator))

    return wrap_output(*lines)


# Convenience functions for common formatting patterns

def header(title, width=70):
    """Quick header formatting."""
    return f"%r{format_header(title, width)}%r"


def footer(width=70):
    """Quick footer formatting."""
    return f"%r{format_footer(width)}%r"


def divider(width=70, char='-'):
    """Quick divider line."""
    return char * width


def blank_line():
    """Return a blank line token."""
    return '%r'


def indent(text, spaces=2):
    """Indent text by specified number of spaces."""
    prefix = ' ' * spaces
    return prefix + text


def color(text, color_code):
    """
    Wrap text in a color code.

    Args:
        text (str): Text to colorize
        color_code (str): Color code (r, g, y, b, m, c, w, x)

    Returns:
        str: Colored text with reset at the end
    """
    return f"%c{color_code}{text}%cn"


def bold(text):
    """Make text bold/highlighted."""
    return f"%ch{text}%cn"
