"""
Script to create the OOC (Out of Character) room.

Run this in-game as a Builder/Admin:
  @py from world.create_ooc_room import create_ooc_room; create_ooc_room()

Or run via Python directly:
  DJANGO_SETTINGS_MODULE=server.conf.settings python -c "import django; django.setup(); from world.create_ooc_room import create_ooc_room; create_ooc_room()"
"""

from evennia.utils.create import create_object
from typeclasses.rooms import OOCRoom


def create_ooc_room():
    """Create the OOC lobby room."""

    # Check if it already exists
    from evennia.objects.models import ObjectDB
    existing = ObjectDB.objects.filter(db_key="OOC Lobby", db_typeclass_path="typeclasses.rooms.OOCRoom").first()
    if existing:
        print(f"OOC Lobby already exists: #{existing.id}")
        print(f"\nTo set as starting location, add to server/conf/settings.py:")
        print(f'START_LOCATION = "#{existing.id}"')
        print(f'DEFAULT_HOME = "#{existing.id}"')
        return existing

    # Create the room
    ooc_room = create_object(
        OOCRoom,
        key="OOC Lobby",
        location=None,  # No parent location
    )

    print(f"Created OOC Lobby: #{ooc_room.id}")
    print(f"\nTo set as starting location, add to server/conf/settings.py:")
    print(f'START_LOCATION = "#{ooc_room.id}"')
    print(f'DEFAULT_HOME = "#{ooc_room.id}"')

    return ooc_room
