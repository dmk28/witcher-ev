"""
Room Building Commands for Witcher RPG.

Includes GM room builder and player room purchase system.
"""

from evennia import Command, create_object
from evennia.utils.search import search_object
from world.witcher_rpg.room_models import WitcherRoom, RoomType, BiomeType, DangerLevel
from world.witcher_rpg.models import WitcherCharacter
import json


class CmdRoomCreate(Command):
    """
    Create a new room (GM only).

    Usage:
      +roomcreate <name>

    Creates a new room at your current location. After creation, use
    +roomedit to configure the room's properties.

    Examples:
      +roomcreate The Rusty Sword Tavern
      +roomcreate Ancient Forest Clearing
    """

    key = "+roomcreate"
    aliases = ["roomcreate"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: +roomcreate <room name>")
            return

        room_name = self.args.strip()

        # Create the Evennia room object
        new_room = create_object(
            "typeclasses.rooms.Room",
            key=room_name,
            location=None
        )

        if not new_room:
            self.caller.msg("|rFailed to create room.|n")
            return

        # Create WitcherRoom data
        witcher_room = WitcherRoom.objects.create(
            room_object=new_room,
            room_type=RoomType.ADVENTURE,
            biome=BiomeType.PLAINS,
            danger_level=DangerLevel.SAFE
        )

        self.caller.msg(
            f"|gRoom created:|n {room_name}\n"
            f"Room ID: #{new_room.id}\n"
            f"Type: {witcher_room.get_room_type_display()}\n"
            f"Biome: {witcher_room.get_biome_display()}\n\n"
            f"Use |w+roomedit here/...|n to configure this room.\n"
            f"Use |w+roomlink <direction> = {room_name}|n to link it to other rooms."
        )


class CmdRoomEdit(Command):
    """
    Edit room properties (GM only).

    Usage:
      +roomedit here/name = <new name>
      +roomedit here/desc = <description>
      +roomedit here/type = adventure|bank|extraction
      +roomedit here/biome = forest|mine|urban|plains|etc
      +roomedit here/purpose = crafting|storage|residence|shop|tavern
      +roomedit here/owner = <character name>
      +roomedit here/organization = <org name>
      +roomedit here/resources = <JSON dict>
      +roomedit here/danger = safe|low|moderate|high|critical
      +roomedit <room name>/... = ...

    Examples:
      +roomedit here/name = The Prancing Pony Inn
      +roomedit here/desc = A cozy tavern with a roaring fireplace.
      +roomedit here/type = bank
      +roomedit here/biome = urban
      +roomedit here/purpose = crafting
      +roomedit here/owner = Geralt
      +roomedit here/resources = {"iron_ore": 50, "wood": 100}
      +roomedit here/danger = moderate
    """

    key = "+roomedit"
    aliases = ["roomedit"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.args or '=' not in self.args:
            self.caller.msg("Usage: +roomedit <room>/property = <value>")
            return

        # Parse arguments
        lhs, rhs = self.args.split('=', 1)
        lhs = lhs.strip()
        value = rhs.strip()

        # Parse room and property
        if '/' not in lhs:
            self.caller.msg("Usage: +roomedit <room>/property = <value>")
            return

        room_str, property_name = lhs.split('/', 1)
        room_str = room_str.strip()
        property_name = property_name.strip().lower()

        # Get room
        if room_str.lower() == 'here':
            room = self.caller.location
        else:
            matches = search_object(room_str)
            if not matches:
                self.caller.msg(f"Room '{room_str}' not found.")
                return
            room = matches[0]

        if not room:
            self.caller.msg("You must be in a room or specify a valid room name.")
            return

        # Get WitcherRoom
        try:
            witcher_room = WitcherRoom.objects.get(room_object=room)
        except WitcherRoom.DoesNotExist:
            self.caller.msg("This room doesn't have Witcher RPG data. Use +roomcreate first.")
            return

        # Handle different properties
        if property_name == 'name':
            room.key = value
            self.caller.msg(f"Room name set to: {value}")

        elif property_name == 'desc' or property_name == 'description':
            room.db.desc = value
            self.caller.msg(f"Room description set.")

        elif property_name == 'type':
            valid_types = {
                'adventure': RoomType.ADVENTURE,
                'bank': RoomType.BANK,
                'extraction': RoomType.EXTRACTION
            }
            if value.lower() not in valid_types:
                self.caller.msg(f"Invalid type. Valid types: {', '.join(valid_types.keys())}")
                return
            witcher_room.room_type = valid_types[value.lower()]
            witcher_room.save()
            self.caller.msg(f"Room type set to: {value}")

        elif property_name == 'biome':
            valid_biomes = [choice[0] for choice in BiomeType.choices]
            if value.lower() not in valid_biomes:
                self.caller.msg(f"Invalid biome. Valid biomes: {', '.join(valid_biomes)}")
                return
            witcher_room.biome = value.lower()
            witcher_room.save()
            self.caller.msg(f"Biome set to: {value}")

        elif property_name == 'purpose':
            valid_purposes = ['crafting', 'storage', 'residence', 'shop', 'tavern']
            if value.lower() not in valid_purposes:
                self.caller.msg(f"Invalid purpose. Valid purposes: {', '.join(valid_purposes)}")
                return
            witcher_room.room_purpose = value.lower()
            witcher_room.save()
            self.caller.msg(f"Room purpose set to: {value}")

        elif property_name == 'owner':
            # Find character
            owner = search_object(value)
            if not owner:
                self.caller.msg(f"Character '{value}' not found.")
                return
            witcher_room.owner = owner[0]
            witcher_room.save()
            self.caller.msg(f"Room owner set to: {owner[0].key}")

        elif property_name == 'organization':
            witcher_room.organization = value
            witcher_room.save()
            self.caller.msg(f"Organization set to: {value}")

        elif property_name == 'resources':
            try:
                resources = json.loads(value)
                if not isinstance(resources, dict):
                    raise ValueError("Resources must be a JSON dictionary")
                witcher_room.available_resources = resources
                witcher_room.save()
                self.caller.msg(f"Resources set to: {resources}")
            except (json.JSONDecodeError, ValueError) as e:
                self.caller.msg(f"|rInvalid JSON format:|n {e}")
                return

        elif property_name == 'danger':
            valid_dangers = [choice[0] for choice in DangerLevel.choices]
            if value.lower() not in valid_dangers:
                self.caller.msg(f"Invalid danger level. Valid levels: {', '.join(valid_dangers)}")
                return
            witcher_room.danger_level = value.lower()
            witcher_room.save()
            self.caller.msg(f"Danger level set to: {value}")

        else:
            self.caller.msg(
                f"|rUnknown property:|n {property_name}\n"
                "Valid properties: name, desc, type, biome, purpose, owner, organization, resources, danger"
            )


class CmdRoomLink(Command):
    """
    Create an exit between rooms (GM only).

    Usage:
      +roomlink <direction> = <target room>
      +roomlink/twoway <direction> = <target room>

    Creates a one-way exit from your current location to the target room.
    Use /twoway to create exits in both directions.

    Examples:
      +roomlink north = Town Square
      +roomlink/twoway east = Ancient Forest
    """

    key = "+roomlink"
    aliases = ["roomlink"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.args or '=' not in self.args:
            self.caller.msg("Usage: +roomlink <direction> = <target room>")
            return

        direction, target_name = self.args.split('=', 1)
        direction = direction.strip().lower()
        target_name = target_name.strip()

        # Get current room
        current_room = self.caller.location
        if not current_room:
            self.caller.msg("You must be in a room to create exits.")
            return

        # Find target room
        target_matches = search_object(target_name)
        if not target_matches:
            self.caller.msg(f"Target room '{target_name}' not found.")
            return
        target_room = target_matches[0]

        # Create exit
        exit_obj = create_object(
            "typeclasses.exits.Exit",
            key=direction,
            location=current_room,
            destination=target_room
        )

        if not exit_obj:
            self.caller.msg(f"|rFailed to create exit.|n")
            return

        self.caller.msg(
            f"|gExit created:|n {direction} from {current_room.key} to {target_room.key}"
        )

        # Create return exit if /twoway
        if 'twoway' in self.switches:
            # Determine opposite direction
            opposites = {
                'north': 'south', 'south': 'north',
                'east': 'west', 'west': 'east',
                'northeast': 'southwest', 'southwest': 'northeast',
                'northwest': 'southeast', 'southeast': 'northwest',
                'up': 'down', 'down': 'up',
                'in': 'out', 'out': 'in'
            }

            opposite = opposites.get(direction)
            if opposite:
                return_exit = create_object(
                    "typeclasses.exits.Exit",
                    key=opposite,
                    location=target_room,
                    destination=current_room
                )
                if return_exit:
                    self.caller.msg(
                        f"|gReturn exit created:|n {opposite} from {target_room.key} to {current_room.key}"
                    )
            else:
                self.caller.msg(f"|yNo automatic opposite for '{direction}'. Create return exit manually.|n")


class CmdRoomDelete(Command):
    """
    Delete a room (GM only).

    Usage:
      +roomdelete here
      +roomdelete <room name>

    Permanently deletes a room and its associated WitcherRoom data.
    All exits leading to this room will also be deleted.

    WARNING: This action cannot be undone!
    """

    key = "+roomdelete"
    aliases = ["roomdelete"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: +roomdelete <room name> or +roomdelete here")
            return

        room_str = self.args.strip()

        # Get room
        if room_str.lower() == 'here':
            room = self.caller.location
        else:
            matches = search_object(room_str)
            if not matches:
                self.caller.msg(f"Room '{room_str}' not found.")
                return
            room = matches[0]

        if not room:
            self.caller.msg("Room not found.")
            return

        room_name = room.key

        # Delete WitcherRoom data if exists
        try:
            witcher_room = WitcherRoom.objects.get(room_object=room)
            witcher_room.delete()
        except WitcherRoom.DoesNotExist:
            pass

        # Delete the room
        room.delete()

        self.caller.msg(f"|rRoom deleted:|n {room_name}")


# ============================================================================
# PLAYER ROOM BUILDING
# ============================================================================


class CmdBuyRoom(Command):
    """
    Purchase a new room (costs 50,000 gold).

    Usage:
      +buyroom <room name>

    Purchases a new room that you own. The room will be created in an
    urban area and you can customize its purpose for crafting, storage,
    or residence.

    Cost: 50,000 gold crowns

    Examples:
      +buyroom Geralt's Workshop
      +buyroom My Cozy Apartment
    """

    key = "+buyroom"
    aliases = ["buyroom", "purchaseroom"]
    locks = "cmd:all()"
    help_category = "Economy"

    ROOM_COST = 50000

    def func(self):
        caller = self.caller

        if not self.args:
            self.caller.msg(
                "Usage: +buyroom <room name>\n\n"
                f"Cost: {self.ROOM_COST:,} gold crowns\n"
                "The room will be created in an urban area and you can set its purpose."
            )
            return

        room_name = self.args.strip()

        # Get character
        try:
            character = WitcherCharacter.objects.get(db_object=caller)
        except WitcherCharacter.DoesNotExist:
            caller.msg("|rYou don't have a character yet.|n")
            return

        # Check gold
        if character.gold < self.ROOM_COST:
            caller.msg(
                f"|rInsufficient gold!|n\n"
                f"Your gold: {character.gold:,}\n"
                f"Required: {self.ROOM_COST:,} crowns\n"
                f"Short by: {self.ROOM_COST - character.gold:,} crowns"
            )
            return

        # Create the room
        new_room = create_object(
            "typeclasses.rooms.Room",
            key=room_name,
            location=None
        )

        if not new_room:
            caller.msg("|rFailed to create room. Contact a GM.|n")
            return

        # Create WitcherRoom data
        witcher_room = WitcherRoom.objects.create(
            room_object=new_room,
            room_type=RoomType.ADVENTURE,
            biome=BiomeType.URBAN,
            danger_level=DangerLevel.SAFE,
            owner=caller,
            room_purpose='residence'  # Default to residence
        )

        # Deduct gold
        character.gold -= self.ROOM_COST
        character.save()

        caller.msg(
            "=" * 70 + "\n"
            "|gRoom Purchased!|n\n" +
            "=" * 70 + "\n"
            f"Room Name: {room_name}\n"
            f"Room ID: #{new_room.id}\n"
            f"Cost: {self.ROOM_COST:,} gold crowns\n"
            f"Remaining Gold: {character.gold:,} crowns\n\n"
            f"Location: Urban area (default)\n"
            f"Purpose: Residence (default)\n"
            f"Danger: Safe\n\n"
            "Use |w+roompurpose {room_name} = <purpose>|n to set the room purpose.\n"
            "Valid purposes: crafting, storage, residence\n\n"
            "Use |w+roomlink <direction> = {room_name}|n to link this room to others.\n"
            "(You'll need GM permission to link to public areas)\n\n"
            "Use |w+myrooms|n to see all your owned rooms.\n" +
            "=" * 70
        )


class CmdMyRooms(Command):
    """
    List all rooms you own.

    Usage:
      +myrooms

    Shows all rooms you've purchased, their purposes, and IDs.
    """

    key = "+myrooms"
    aliases = ["myrooms", "ownedrooms"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller

        # Get owned rooms
        owned_rooms = WitcherRoom.objects.filter(owner=caller).order_by('created_date')

        if not owned_rooms.exists():
            caller.msg(
                "You don't own any rooms.\n\n"
                "Use |w+buyroom <name>|n to purchase a room (50,000 gold)."
            )
            return

        lines = []
        lines.append("=" * 70)
        lines.append("Your Owned Rooms")
        lines.append("=" * 70)
        lines.append(f"{'Room Name':<30} {'Purpose':<15} {'ID':<5}")
        lines.append("-" * 70)

        for wr in owned_rooms:
            room_name = wr.room_object.key[:28]
            purpose = wr.room_purpose if wr.room_purpose else 'none'
            room_id = wr.room_object.id

            lines.append(f"{room_name:<30} {purpose:<15} #{room_id:<5}")

        lines.append("=" * 70)
        lines.append(f"Total Rooms: {owned_rooms.count()}")
        lines.append(f"Total Investment: {owned_rooms.count() * 50000:,} gold crowns")
        lines.append("=" * 70)

        caller.msg("\n".join(lines))


class CmdRoomPurpose(Command):
    """
    Set the purpose of a room you own.

    Usage:
      +roompurpose <room name> = <purpose>

    Valid purposes:
      crafting  - Enables crafting in this room (acts as workshop)
      storage   - Enables bank storage access
      residence - For roleplay and decoration

    Examples:
      +roompurpose My Workshop = crafting
      +roompurpose Storage Vault = storage
      +roompurpose Cozy Home = residence
    """

    key = "+roompurpose"
    aliases = ["roompurpose", "setpurpose"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller

        if not self.args or '=' not in self.args:
            caller.msg(
                "Usage: +roompurpose <room name> = <purpose>\n\n"
                "Valid purposes: crafting, storage, residence"
            )
            return

        room_name, purpose = self.args.split('=', 1)
        room_name = room_name.strip()
        purpose = purpose.strip().lower()

        # Validate purpose
        valid_purposes = ['crafting', 'storage', 'residence']
        if purpose not in valid_purposes:
            caller.msg(
                f"|rInvalid purpose:|n {purpose}\n"
                f"Valid purposes: {', '.join(valid_purposes)}"
            )
            return

        # Find room
        matches = search_object(room_name)
        if not matches:
            caller.msg(f"Room '{room_name}' not found.")
            return

        room = matches[0]

        # Get WitcherRoom
        try:
            witcher_room = WitcherRoom.objects.get(room_object=room)
        except WitcherRoom.DoesNotExist:
            caller.msg("This room doesn't have Witcher RPG data.")
            return

        # Check ownership
        if witcher_room.owner != caller:
            caller.msg("|rYou don't own this room!|n")
            return

        # Set purpose
        witcher_room.room_purpose = purpose
        witcher_room.save()

        caller.msg(
            f"|gRoom purpose updated!|n\n"
            f"Room: {room.key}\n"
            f"Purpose: {purpose}\n\n" +
            ("|wNote:|n This room now acts as a workshop for crafting.\n" if purpose == 'crafting' else "") +
            ("|wNote:|n This room now provides bank storage access.\n" if purpose == 'storage' else "") +
            ("|wNote:|n This room is set up as a residence for roleplay.\n" if purpose == 'residence' else "")
        )


class CmdSellRoom(Command):
    """
    Sell a room you own (50% refund).

    Usage:
      +sellroom <room name>

    Sells a room back for 25,000 gold (50% of purchase price).
    The room will be deleted permanently.

    WARNING: This action cannot be undone!

    Examples:
      +sellroom Old Workshop
    """

    key = "+sellroom"
    aliases = ["sellroom"]
    locks = "cmd:all()"
    help_category = "Economy"

    REFUND_AMOUNT = 25000

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg(
                "Usage: +sellroom <room name>\n\n"
                f"Refund: {self.REFUND_AMOUNT:,} gold (50% of purchase price)\n"
                "|rWARNING:|n This permanently deletes the room!"
            )
            return

        room_name = self.args.strip()

        # Get character
        try:
            character = WitcherCharacter.objects.get(db_object=caller)
        except WitcherCharacter.DoesNotExist:
            caller.msg("|rYou don't have a character yet.|n")
            return

        # Find room
        matches = search_object(room_name)
        if not matches:
            caller.msg(f"Room '{room_name}' not found.")
            return

        room = matches[0]

        # Get WitcherRoom
        try:
            witcher_room = WitcherRoom.objects.get(room_object=room)
        except WitcherRoom.DoesNotExist:
            caller.msg("This room doesn't have Witcher RPG data.")
            return

        # Check ownership
        if witcher_room.owner != caller:
            caller.msg("|rYou don't own this room!|n")
            return

        # Delete room
        actual_name = room.key
        witcher_room.delete()
        room.delete()

        # Add gold
        character.gold += self.REFUND_AMOUNT
        character.save()

        caller.msg(
            "=" * 70 + "\n"
            "|yRoom Sold|n\n" +
            "=" * 70 + "\n"
            f"Room: {actual_name}\n"
            f"Refund: {self.REFUND_AMOUNT:,} gold crowns\n"
            f"New Gold Total: {character.gold:,} crowns\n" +
            "=" * 70
        )
