# MUSH Formatting Guide

This guide explains how to use MUSH-style text formatting in the Witcher RPG codebase.

## Overview

The codebase supports MUSH/MUX-style formatting tokens for consistent text presentation across in-game and web interfaces. All formatting is handled through the `world/witcher_rpg/mush_utils.py` module.

## MUSH Tokens

### Basic Formatting

| Token | Description | Converts To (In-Game) |
|-------|-------------|----------------------|
| `%r` or `%R` | Carriage return (newline) | `\n` |
| `%t` or `%T` | Tab (4 spaces) | `    ` |
| `%b` or `%B` | Single space | ` ` |

### Color Codes

| Token | Description | Converts To (In-Game) |
|-------|-------------|----------------------|
| `%cr` | Red color | `\|r` |
| `%cg` | Green color | `\|g` |
| `%cy` | Yellow color | `\|y` |
| `%cb` | Blue color | `\|b` |
| `%cm` | Magenta color | `\|m` |
| `%cc` | Cyan color | `\|c` |
| `%cw` | White color | `\|w` |
| `%cx` | Black color | `\|x` |
| `%cn` | Reset color | `\|n` |
| `%ch` | Highlight/Bold | `\|h` |

**Note:** All color tokens support uppercase variants (e.g., `%cR`, `%cG`).

## Usage in Commands

### Basic Example

```python
from world.witcher_rpg.mush_utils import convert_mush_tokens

def func(self):
    caller = self.caller

    lines = []
    lines.append("%r")  # Blank line at start
    lines.append("=" * 70)
    lines.append("Character Information")
    lines.append("=" * 70)
    lines.append("%r")

    lines.append(f"|wName:|n {character.name}")
    lines.append(f"|wLevel:|n {character.level}")
    lines.append("%r")

    lines.append("=" * 70)
    lines.append("%r")

    # Convert tokens and send
    caller.msg(convert_mush_tokens("%r".join(lines)))
```

### Using Tabs for Indentation

```python
lines = []
lines.append("|wIncome Information:|n")
lines.append(f"%t%tBase Multiplier: {multiplier}x")
lines.append(f"%t%tMember Tithing: {percentage}%")
lines.append("%r")

caller.msg(convert_mush_tokens("%r".join(lines)))
```

**Output:**
```
Income Information:
        Base Multiplier: 2.0x
        Member Tithing: 10%

```

### Color Formatting

```python
# Using MUSH color codes
lines.append("%cgSuccess!%cn Your item was crafted.")
lines.append("%crError!%cn Something went wrong.")
lines.append("%cyWarning:%cn Low on materials.")

# Or mix with Evennia codes
lines.append("|gSuccess!|n Your item was crafted.")
```

## Helper Functions

The `mush_utils` module provides several helper functions:

### format_header()

```python
from world.witcher_rpg.mush_utils import format_header

header = format_header("Character Sheet", width=70, fill_char='=')
# Returns: "======================================================================%rCharacter Sheet%r======================================================================"
```

### format_table_row()

```python
from world.witcher_rpg.mush_utils import format_table_row

row = format_table_row("Geralt", "Witcher", "Level 5", widths=[20, 15, 10])
# Returns: "Geralt              Witcher        Level 5   "
```

### mush_table()

```python
from world.witcher_rpg.mush_utils import mush_table

headers = ["Name", "Rank", "Income"]
rows = [
    ("Geralt", "2", "300 crowns"),
    ("Yennefer", "3", "800 crowns"),
]

table = mush_table(headers, rows, widths=[20, 8, 15])
caller.msg(convert_mush_tokens(table))
```

### wrap_output()

```python
from world.witcher_rpg.mush_utils import wrap_output

output = wrap_output(
    "=" * 70,
    "Title Here",
    "=" * 70,
    "",
    "Content line 1",
    "Content line 2"
)
# Joins all with %r tokens
```

### Convenience Functions

```python
from world.witcher_rpg.mush_utils import header, footer, divider, color, bold

# Quick header with padding
output = header("My Section", width=70)

# Quick footer
output = footer(width=70)

# Divider line
output = divider(width=70, char='-')

# Colorize text
text = color("Important!", "r")  # Red text with reset
text = bold("Emphasis")  # Highlighted text
```

## Web Integration

The `process_mush_text()` function handles conversion for web display:

```python
from world.witcher_rpg.mush_utils import process_mush_text

# For web output
html_text = process_mush_text(mush_text, for_web=True)
# %r -> <br>
# %t -> &nbsp;&nbsp;&nbsp;&nbsp;
# %cr -> <span style="color: #ff0000;">

# For in-game output (default)
game_text = process_mush_text(mush_text, for_web=False)
# %r -> \n
# %t -> four spaces
# %cr -> |r
```

## Best Practices

### 1. Use %r for Line Breaks

**Do:**
```python
lines = []
lines.append("%r")
lines.append("Header")
lines.append("%r")
caller.msg(convert_mush_tokens("%r".join(lines)))
```

**Don't:**
```python
caller.msg("\n\nHeader\n\n")  # Not MUSH-compatible
```

### 2. Use %t for Indentation

**Do:**
```python
lines.append(f"%t%tIndented text")  # Two tabs
```

**Don't:**
```python
lines.append(f"  Indented text")  # Hard-coded spaces
```

### 3. Always Convert Before Sending

**Do:**
```python
caller.msg(convert_mush_tokens("%r".join(lines)))
```

**Don't:**
```python
caller.msg("%r".join(lines))  # Tokens won't be processed
```

### 4. Structure Output Consistently

```python
def func(self):
    lines = []

    # Opening blank line
    lines.append("%r")

    # Header section
    lines.append("=" * 70)
    lines.append("Title")
    lines.append("=" * 70)
    lines.append("%r")

    # Content section
    lines.append("Content here")
    lines.append("%r")

    # Footer section
    lines.append("=" * 70)

    # Closing blank line
    lines.append("%r")

    caller.msg(convert_mush_tokens("%r".join(lines)))
```

## Legacy Code Conversion

When updating existing commands to use MUSH formatting:

### Before (Plain Python)
```python
caller.msg("\n" + "=" * 70)
caller.msg("Title")
caller.msg("=" * 70 + "\n")
caller.msg("  Content")
```

### After (MUSH Style)
```python
lines = []
lines.append("%r")
lines.append("=" * 70)
lines.append("Title")
lines.append("=" * 70)
lines.append("%r")
lines.append("%t%tContent")

caller.msg(convert_mush_tokens("%r".join(lines)))
```

## Command Output Template

Use this template for new commands:

```python
from evennia import Command
from world.witcher_rpg.mush_utils import convert_mush_tokens

class CmdExample(Command):
    """
    Example command with MUSH formatting.

    Usage:
      example
    """

    key = "example"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        lines = []
        lines.append("%r")
        lines.append("=" * 70)
        lines.append("Command Output Title")
        lines.append("=" * 70)
        lines.append("%r")

        # Main content
        lines.append("|wSection Header:|n")
        lines.append(f"%t%tDetail 1: Value")
        lines.append(f"%t%tDetail 2: Value")
        lines.append("%r")

        # Another section
        lines.append("|wAnother Section:|n")
        lines.append("Content here")
        lines.append("%r")

        # Footer
        lines.append("=" * 70)
        lines.append("%r")

        caller.msg(convert_mush_tokens("%r".join(lines)))
```

## Compatibility Notes

- **Evennia color codes** (`|r`, `|g`, etc.) still work and can be mixed with MUSH tokens
- **Web display** automatically converts MUSH tokens to HTML via `process_mush_text(text, for_web=True)`
- **Case insensitive** - `%r`, `%R`, `%t`, `%T` all work the same
- **No parsing needed** for plain text - only use `convert_mush_tokens()` when you have MUSH tokens

## Testing

To test MUSH formatting:

```python
from world.witcher_rpg.mush_utils import convert_mush_tokens

# Test string
test = "%r%cgGreen text%cn and %crred text%cn%r%t%tIndented"

# Convert and print
print(convert_mush_tokens(test))
```

## Files Using MUSH Formatting

Current files with MUSH formatting:
- `commands/income_commands.py` - All organization/income commands
- Additional commands to be converted as needed

## Future Enhancements

Planned features:
- `%xh` - ANSI escape sequences
- `%i` - Inverse colors
- `%u` - Underline
- Configurable tab width
- Custom color palette support
