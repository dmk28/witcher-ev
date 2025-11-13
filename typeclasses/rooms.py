"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.utils.utils import inherits_from

from .objects import ObjectParent


# Color codes for different areas (using truecolor for rich visuals)
AREA_COLORS = {
    # Vengerberg areas - Rich medieval colors
    'temple_district': '|#FFD700',      # Gold - sacred and wealthy
    'royal_quarter': '|#9370DB',        # Medium Purple - royal elegance
    'market_ward': '|#FF8C00',          # Dark Orange - bustling commerce
    'craftsmen_quarter': '|#CD5C5C',    # Indian Red - forge fires
    'river_ward': '|#4682B4',           # Steel Blue - water trade
    'northern_woods': '|#228B22',       # Forest Green - wilderness
    'western_woods': '|#2F4F2F',        # Dark Slate Gray - dangerous forest
    'iron_mine': '|#B8860B',            # Dark Goldenrod - ore and earth
    'northern_approach': '|#D3D3D3',    # Light Gray - traveled roads
    'western_approach': '|#A9A9A9',     # Dark Gray - lesser roads
    'eastern_river': '|#00CED1',        # Dark Turquoise - Pontar River
    'southern_farmlands': '|#9ACD32',   # Yellow Green - fertile fields
    'southern_river': '|#5F9EA0',       # Cadet Blue - quieter waters

    # Novigrad areas - Darker, grimier city colors
    'temple_district': '|#DAA520',      # Goldenrod - Eternal Fire's gold
    'gildorf': '|#00CED1',              # Dark Turquoise - wealthy merchant cyan
    'the_bits': '|#8B0000',             # Dark Red - poverty and blood
    'harborside': '|#1E90FF',           # Dodger Blue - vast ocean port
    'glory_lane': '|#FF1493',           # Deep Pink - vice and pleasure
    'putrid_grove': '|#2F2F2F',         # Very Dark Gray - death and graves
    'oxenfurt_gate': '|#32CD32',        # Lime Green - scholarly route
    'tretogor_gate': '|#FFD700',        # Gold - Redanian influence
    'northern_swamps': '|#556B2F',      # Dark Olive Green - murky swamps
    'western_forests': '|#228B22',      # Forest Green - trade route woods
    'eastern_coast': '|#4169E1',        # Royal Blue - ocean coastline
}


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    Enhanced to:
    - Process MUSH formatting tokens (%r, %t, etc.)
    - Color-code room names by area
    - Display area type in room header
    """

    def return_appearance(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.

        Returns:
            str: The formatted description.
        """
        if not looker:
            return ""

        # Get the base appearance
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))

        # Get room name with color coding
        room_name = self.get_display_name(looker)

        # Add area indicator if we have one
        area = self.db.area
        if area:
            area_display = area.replace('_', ' ').title()
            room_name = f"{room_name} |w[{area_display}]|n"

        # Process description for MUSH tokens
        desc = self.db.desc
        if desc:
            desc = self.process_mush_formatting(desc)
        else:
            desc = "You see nothing special."

        # Build the string
        string = f"|c{room_name}|n\n"
        string += desc

        # Add exits
        exits = [ex for ex in self.exits if ex.access(looker, "view")]
        if exits:
            exit_names = ", ".join(ex.name for ex in exits)
            string += f"\n|wExits:|n {exit_names}"

        # Add visible objects
        vis_objs = [con for con in visible if not inherits_from(con, "evennia.objects.objects.DefaultExit")]
        if vis_objs:
            obj_names = ", ".join(obj.get_display_name(looker) for obj in vis_objs)
            string += f"\n|wYou see:|n {obj_names}"

        return string

    def get_display_name(self, looker, **kwargs):
        """
        Get the display name of the room with color coding based on area.

        Args:
            looker (Object): The object looking.
            **kwargs: Arbitrary data.

        Returns:
            str: The color-coded room name.
        """
        # Use display_name if set, otherwise use key
        name = self.db.display_name or self.key

        # Check if already has color codes (Novigrad rooms)
        if self.db.color:
            return name  # Already has color from builder

        # Add color based on area (Vengerberg rooms)
        area = self.db.area
        if area and area in AREA_COLORS:
            color = AREA_COLORS[area]
            # Strip any existing color codes and re-add
            name = name.strip('|n')
            return f"{color}{name}|n"

        return name

    def process_mush_formatting(self, text):
        """
        Process MUSH formatting tokens in text.

        Args:
            text (str): Text with MUSH tokens like %r, %t, etc.

        Returns:
            str: Text with tokens converted to Evennia formatting.
        """
        if not text:
            return text

        # Convert MUSH tokens to Evennia equivalents
        conversions = {
            '%r': '\n',
            '%R': '\n',
            '%t': '    ',  # Tab = 4 spaces
            '%T': '    ',
            '%b': ' ',
            '%B': ' ',
            '%cr': '|r',   # Red
            '%cR': '|R',   # Bright red
            '%cg': '|g',   # Green
            '%cG': '|G',   # Bright green
            '%cy': '|y',   # Yellow
            '%cY': '|Y',   # Bright yellow
            '%cb': '|b',   # Blue
            '%cB': '|B',   # Bright blue
            '%cm': '|m',   # Magenta
            '%cM': '|M',   # Bright magenta
            '%cc': '|c',   # Cyan
            '%cC': '|C',   # Bright cyan
            '%cw': '|w',   # White
            '%cW': '|W',   # Bright white
            '%cx': '|x',   # Black
            '%cX': '|X',   # Bright black
            '%cn': '|n',   # Reset
            '%ch': '|h',   # Highlight
        }

        for token, replacement in conversions.items():
            text = text.replace(token, replacement)

        return text
