"""
Room management commands for Witcher RPG.
Handles room setup, workshop creation, and room ownership.
"""

from evennia import Command
from world.witcher_rpg.room_models import WitcherRoom


class CmdRoom(Command):
    """
    Manage room properties and setup.

    Usage:
      room                             - View current room info
      room/owner <character>           - Set room owner (Builder+)
      room/purpose <purpose>           - Set room purpose (Builder+)
      room/biome <biome>               - Set room biome (Builder+)

    Room purposes:
      crafting  - Crafting Workshop (requires urban biome + ownership)
      storage   - Storage/Warehouse
      residence - Residence
      shop      - Shop/Merchant
      tavern    - Tavern/Inn

    Biomes:
      forest, mine, hills, river, ocean, plains, mountains, swamp, desert, urban

    Examples:
      room/biome urban
      room/owner Geralt
      room/purpose crafting

    Note: Crafting workshops must be in urban biomes and have an owner.
    """

    key = "room"
    aliases = []
    locks = "cmd:all()"
    help_category = "Building"

    def func(self):
        caller = self.caller

        if not caller.location:
            caller.msg("You must be in a location to use this command.")
            return

        # Get or create WitcherRoom
        try:
            witcher_room = WitcherRoom.objects.get(room_object=caller.location)
        except WitcherRoom.DoesNotExist:
            if not caller.check_permstring("Builder"):
                caller.msg("|rThis location has not been set up as a Witcher room yet. Contact a Builder.|n")
                return

            # Create new witcher room
            witcher_room = WitcherRoom.objects.create(
                room_object=caller.location
            )
            caller.msg("|gCreated Witcher room data for this location.|n")

        # View room info
        if not self.switches:
            self._view_room(witcher_room)
            return

        # Set owner
        if 'owner' in self.switches:
            self._set_owner(witcher_room)
            return

        # Set purpose
        if 'purpose' in self.switches:
            self._set_purpose(witcher_room)
            return

        # Set biome
        if 'biome' in self.switches:
            self._set_biome(witcher_room)
            return

        caller.msg("Invalid room command. See 'help room'.")

    def _view_room(self, witcher_room):
        """Display current room information."""
        output = []
        output.append("|w" + "=" * 70 + "|n")
        output.append("|w" + f"{'Room Information':^70}" + "|n")
        output.append("|w" + "=" * 70 + "|n")
        output.append(f"|yRoom:|n {self.caller.location.db_key}")
        output.append(f"|yType:|n {witcher_room.get_room_type_display()}")
        output.append(f"|yBiome:|n {witcher_room.get_biome_display()}")
        output.append(f"|yDanger Level:|n {witcher_room.get_danger_level_display()}")

        if witcher_room.owner:
            output.append(f"|yOwner:|n {witcher_room.owner.db_key}")
        else:
            output.append(f"|yOwner:|n None")

        if witcher_room.room_purpose:
            output.append(f"|yPurpose:|n {witcher_room.get_room_purpose_display()}")
        else:
            output.append(f"|yPurpose:|n None")

        if witcher_room.organization:
            output.append(f"|yOrganization:|n {witcher_room.organization}")

        # Workshop status
        if witcher_room.room_purpose == 'crafting':
            is_valid, reason = witcher_room.is_valid_workshop(self.caller)
            if is_valid:
                output.append(f"\n|g✓ This is a valid crafting workshop for you.|n")
            else:
                output.append(f"\n|r✗ Workshop issue:|n {reason}")

        output.append("|w" + "=" * 70 + "|n")
        self.caller.msg("\n".join(output))

    def _set_owner(self, witcher_room):
        """Set room owner (Builder+ only)."""
        if not self.caller.check_permstring("Builder"):
            self.caller.msg("|rOnly Builders can set room ownership.|n")
            return

        if not self.args:
            self.caller.msg("Usage: room/owner <character name>")
            return

        character_name = self.args.strip()

        # Find character
        target = self.caller.search(character_name, global_search=True)
        if not target:
            return

        # Set owner
        witcher_room.owner = target
        witcher_room.save()

        self.caller.msg(f"|gSet room owner to {target.db_key}.|n")
        self.caller.location.msg_contents(
            f"|y{self.caller.name} has designated {target.db_key} as the owner of this room.|n",
            exclude=self.caller
        )

    def _set_purpose(self, witcher_room):
        """Set room purpose (Builder+ only)."""
        if not self.caller.check_permstring("Builder"):
            self.caller.msg("|rOnly Builders can set room purpose.|n")
            return

        if not self.args:
            self.caller.msg("Usage: room/purpose <purpose>")
            self.caller.msg("Valid purposes: crafting, storage, residence, shop, tavern")
            return

        purpose = self.args.strip().lower()

        # Validate purpose
        valid_purposes = ['crafting', 'storage', 'residence', 'shop', 'tavern', 'none', '']
        if purpose not in valid_purposes:
            self.caller.msg(f"|rInvalid purpose '{purpose}'. Valid: {', '.join(valid_purposes)}|n")
            return

        # Convert 'none' to empty string
        if purpose == 'none':
            purpose = ''

        # Check workshop requirements
        if purpose == 'crafting':
            if witcher_room.biome != 'urban':
                self.caller.msg("|rWarning: Crafting workshops should be in urban biomes.|n")
                self.caller.msg("|rUse 'room/biome urban' first.|n")
                return

            if not witcher_room.owner:
                self.caller.msg("|rWarning: Crafting workshops require an owner.|n")
                self.caller.msg("|rUse 'room/owner <name>' first.|n")
                return

        # Set purpose
        witcher_room.room_purpose = purpose
        witcher_room.save()

        if purpose:
            self.caller.msg(f"|gSet room purpose to '{purpose}'.|n")
        else:
            self.caller.msg("|gCleared room purpose.|n")

    def _set_biome(self, witcher_room):
        """Set room biome (Builder+ only)."""
        if not self.caller.check_permstring("Builder"):
            self.caller.msg("|rOnly Builders can set room biome.|n")
            return

        if not self.args:
            self.caller.msg("Usage: room/biome <biome>")
            self.caller.msg("Valid biomes: forest, mine, hills, river, ocean, plains, mountains, swamp, desert, urban")
            return

        biome = self.args.strip().lower()

        # Validate biome
        valid_biomes = ['forest', 'mine', 'hills', 'river', 'ocean', 'plains', 'mountains', 'swamp', 'desert', 'urban']
        if biome not in valid_biomes:
            self.caller.msg(f"|rInvalid biome '{biome}'. Valid: {', '.join(valid_biomes)}|n")
            return

        # Set biome
        witcher_room.biome = biome
        witcher_room.save()

        self.caller.msg(f"|gSet room biome to '{biome}'.|n")
