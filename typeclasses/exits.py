"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.

    Enhanced to automatically add single-letter aliases for cardinal directions.
    """

    def at_object_creation(self):
        """
        Called when exit is first created.
        Automatically adds short aliases for cardinal directions.
        """
        super().at_object_creation()

        # Mapping of direction names to their single-letter aliases
        direction_aliases = {
            'north': ['n'],
            'south': ['s'],
            'east': ['e'],
            'west': ['w'],
            'northeast': ['ne'],
            'northwest': ['nw'],
            'southeast': ['se'],
            'southwest': ['sw'],
            'up': ['u'],
            'down': ['d'],
            'out': ['o'],
            'in': ['i'],
            'enter': ['en'],
            'leave': ['l'],
        }

        # Add alias if this is a standard direction
        direction = self.key.lower()
        if direction in direction_aliases:
            self.aliases.add(direction_aliases[direction])
