"""
Navigation commands for coordinate-based movement.
"""

from evennia import Command
from evennia.objects.models import ObjectDB


class CmdCoords(Command):
    """
    Show current coordinates or find a room by coordinates.

    Usage:
      coords
      coords <row>,<col>
      coords <row> <col>
      coords find <row>,<col>

    Examples:
      coords              - Show your current coordinates
      coords 18,16        - Show info about room at (18,16)
      coords find 20 15   - Calculate path to room at (20,15)

    All rooms in Vengerberg and Novigrad have grid coordinates.
    Use this to navigate the cities more easily.
    """

    key = "coords"
    aliases = ["coordinates", "coord", "where"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Execute the coords command."""
        caller = self.caller
        location = caller.location

        if not location:
            caller.msg("You are nowhere!")
            return

        # Get current coordinates
        current_coords = location.db.coordinates
        current_city = location.db.city or "unknown"

        if not self.args.strip():
            # Show current coordinates
            if not current_coords:
                caller.msg("This location doesn't have coordinates.")
                return

            row, col = current_coords
            area = location.db.area or "unknown"

            caller.msg(f"|wCurrent Location:|n {location.db.display_name or location.key}")
            caller.msg(f"|wCoordinates:|n ({row}, {col})")
            caller.msg(f"|wCity:|n {current_city.title()}")
            caller.msg(f"|wArea:|n {area.replace('_', ' ').title()}")
            return

        # Parse arguments
        args = self.args.strip().lower()

        # Handle "find" command
        if args.startswith("find "):
            args = args[5:].strip()
            find_mode = True
        else:
            find_mode = False

        # Parse coordinates
        target_coords = None

        # Try "row,col" format
        if ',' in args:
            parts = args.split(',')
            if len(parts) == 2:
                try:
                    row = int(parts[0].strip())
                    col = int(parts[1].strip())
                    target_coords = (row, col)
                except ValueError:
                    pass
        # Try "row col" format
        else:
            parts = args.split()
            if len(parts) == 2:
                try:
                    row = int(parts[0])
                    col = int(parts[1])
                    target_coords = (row, col)
                except ValueError:
                    pass

        if not target_coords:
            caller.msg("|rInvalid coordinates format. Use: coords 18,16 or coords 18 16|n")
            return

        row, col = target_coords

        # Find room at those coordinates
        # Try current city first
        if current_city and current_city != "unknown":
            room_key = f"{current_city}_{row}_{col}"
            target_room = ObjectDB.objects.filter(db_key=room_key).first()
        else:
            target_room = None

        # If not found, try both cities
        if not target_room:
            for city in ['vengerberg', 'novigrad']:
                room_key = f"{city}_{row}_{col}"
                target_room = ObjectDB.objects.filter(db_key=room_key).first()
                if target_room:
                    break

        if not target_room:
            caller.msg(f"|rNo room found at coordinates ({row}, {col})|n")
            caller.msg("|yValid ranges:|n Vengerberg: (0-31, 0-31), Novigrad: (0-39, 0-39)")
            return

        # Show room info
        room_name = target_room.db.display_name or target_room.key
        room_area = target_room.db.area or "unknown"
        room_city = target_room.db.city or "unknown"

        caller.msg(f"|wTarget Room:|n {room_name}")
        caller.msg(f"|wCoordinates:|n ({row}, {col})")
        caller.msg(f"|wCity:|n {room_city.title()}")
        caller.msg(f"|wArea:|n {room_area.replace('_', ' ').title()}")

        # If in find mode, calculate path
        if find_mode and current_coords:
            curr_row, curr_col = current_coords

            # Check if in same city
            if current_city != room_city:
                caller.msg(f"|y\\nTarget is in {room_city.title()}, you are in {current_city.title()}.|n")
                if caller.locks.check_lockstring(caller, "perm(Builder)"):
                    caller.msg("|yUse waystone teleportation to travel between cities.|n")
                return

            # Calculate distance and direction
            row_diff = row - curr_row
            col_diff = col - curr_col

            total_moves = abs(row_diff) + abs(col_diff)

            caller.msg(f"|w\\nDistance:|n {total_moves} moves")

            # Show directions
            directions = []
            if row_diff < 0:
                directions.append(f"north {abs(row_diff)} times")
            elif row_diff > 0:
                directions.append(f"south {abs(row_diff)} times")

            if col_diff < 0:
                directions.append(f"west {abs(col_diff)} times")
            elif col_diff > 0:
                directions.append(f"east {abs(col_diff)} times")

            if directions:
                caller.msg(f"|wPath:|n Go {' and '.join(directions)}")


class CmdGoto(Command):
    """
    Teleport to coordinates (Builder only).

    Usage:
      goto <row>,<col>
      goto <row> <col>
      goto <city> <row>,<col>

    Examples:
      goto 18,16              - Teleport to (18,16) in current city
      goto vengerberg 10,16   - Teleport to Northern Gate in Vengerberg
      goto novigrad 17,25     - Teleport to Hierarch Square in Novigrad

    Builders can use this to quickly navigate to any coordinates.
    """

    key = "goto"
    aliases = ["@goto", "teleport"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        """Execute goto command."""
        caller = self.caller

        if not self.args.strip():
            caller.msg("Usage: goto <row>,<col> or goto <city> <row>,<col>")
            return

        args = self.args.strip().lower()
        parts = args.split()

        # Check if city is specified
        city = None
        coord_str = args

        if parts[0] in ['vengerberg', 'novigrad']:
            city = parts[0]
            coord_str = ' '.join(parts[1:])
        else:
            # Use current location's city
            if caller.location:
                city = caller.location.db.city

        # Parse coordinates
        target_coords = None

        if ',' in coord_str:
            parts = coord_str.split(',')
            if len(parts) == 2:
                try:
                    row = int(parts[0].strip())
                    col = int(parts[1].strip())
                    target_coords = (row, col)
                except ValueError:
                    pass
        else:
            parts = coord_str.split()
            if len(parts) == 2:
                try:
                    row = int(parts[0])
                    col = int(parts[1])
                    target_coords = (row, col)
                except ValueError:
                    pass

        if not target_coords:
            caller.msg("|rInvalid coordinates. Use: goto 18,16 or goto vengerberg 18,16|n")
            return

        row, col = target_coords

        # Find the room
        if not city:
            # Try both cities
            for try_city in ['vengerberg', 'novigrad']:
                room_key = f"{try_city}_{row}_{col}"
                target_room = ObjectDB.objects.filter(db_key=room_key).first()
                if target_room:
                    city = try_city
                    break
        else:
            room_key = f"{city}_{row}_{col}"
            target_room = ObjectDB.objects.filter(db_key=room_key).first()

        if not target_room:
            caller.msg(f"|rNo room found at {city or 'any city'} ({row}, {col})|n")
            return

        # Teleport
        caller.move_to(target_room, quiet=True)

        room_name = target_room.db.display_name or target_room.key
        caller.msg(f"|gTeleported to:|n {room_name}")
        caller.msg(f"|gCoordinates:|n ({row}, {col}) in {city.title()}")

        # Show the room
        caller.execute_cmd("look")
