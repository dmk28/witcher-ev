"""
Simple fix for GameMaster - creates basic objects without circular imports.
Run with: DJANGO_SETTINGS_MODULE=server.conf.settings python world/fix_gamemaster_simple.py
"""

from evennia.utils.create import create_object
from evennia.objects.models import ObjectDB
from evennia.accounts.models import AccountDB
from world.witcher_rpg.models import WitcherCharacter, CharacterStats, CharacterSkills, Vocation

print("\n" + "=" * 70)
print("FIXING GAMEMASTER")
print("=" * 70 + "\n")

# Get GameMaster account
gm = AccountDB.objects.get(username='GameMaster')
print(f"✓ Found GameMaster account (#{gm.id})")

# Create OOC Room as basic Room first (we'll convert typeclass later in-game)
from typeclasses.rooms import Room
existing_ooc = ObjectDB.objects.filter(db_key="OOC Lobby").first()
if existing_ooc:
    ooc_room = existing_ooc
    print(f"✓ OOC Lobby exists (#{ooc_room.id})")
else:
    ooc_room = create_object(
        Room,
        key="OOC Lobby",
        location=None,
    )
    # Set description
    ooc_room.db.desc = (
        "|w=== Welcome to The Northern Kingdoms ===|n\n\n"
        "You are in the Out of Character (OOC) lobby. This is where new\n"
        "players create their characters before entering the game world.\n\n"
        "|yTo create a character:|n\n"
        "  Type |wrequestchar|n to start the interactive character creation\n"
        "  process. You'll choose your vocation, race, stats, skills, and\n"
        "  write a background. A Game Master will review and approve your\n"
        "  character.\n\n"
        "|yTo check your requests:|n\n"
        "  Type |wmyrequests|n to see the status of your character request.\n\n"
        "|yAvailable commands:|n\n"
        "  |wlook|n     - Look around\n"
        "  |wwho|n      - See who's online\n"
        "  |whelp|n     - Get help\n"
        "  |wquit|n     - Disconnect\n\n"
        "Once your character is approved, you'll automatically enter the\n"
        "game world in Vengerberg. Welcome to the Witcher RPG!"
    )
    print(f"✓ Created OOC Lobby (#{ooc_room.id})")

# Get starting location
try:
    start_location = ObjectDB.objects.get(id=595)  # Vengerberg
    print(f"✓ Starting location: {start_location.key}")
except:
    start_location = ooc_room
    print(f"✓ Starting location: OOC Lobby")

# Check for existing character
existing_chars = list(gm.characters.all())
if existing_chars:
    char = existing_chars[0]
    print(f"✓ GameMaster has character: {char.key} (#{char.id})")
else:
    # Create character
    from typeclasses.characters import WitcherCharacter as WitcherCharacterTypeclass

    char = create_object(
        WitcherCharacterTypeclass,
        key="GameMaster",
        location=start_location,
        home=start_location,
    )

    # Create stats
    stats = CharacterStats.objects.create(
        strength=5, agility=5, endurance=5, reflexes=5,
        wit=5, intelligence=5, willpower=5, perception=5,
        charm=5, appearance=5, graces=5, cunning=5
    )

    # Create skills
    skills = CharacterSkills.objects.create(
        blades=5, crafting_type='none', crafting_skill=0
    )

    # Get vocation
    vocation = Vocation.objects.filter(name='soldier').first() or Vocation.objects.first()

    # Create WitcherCharacter
    witcher_char = WitcherCharacter.objects.create(
        db_object=char,
        character_name="GameMaster",
        vocation=vocation,
        stats=stats,
        skills=skills,
        background="Game Master character",
        physical_description="An ethereal presence guiding the world.",
        race='human',
        social_rank=5,
    )

    # Link to account
    gm.characters.add(char)
    char.db.account = gm
    char.permissions.add('Developer')

    print(f"✓ Created character (#{char.id})")

print("\n" + "=" * 70)
print("COMPLETED!")
print("=" * 70)
print(f"\nOOC Lobby ID: #{ooc_room.id}")
print(f"Character ID: #{char.id}")
print("\nNext steps:")
print("1. Add to server/conf/settings.py:")
print(f'   START_LOCATION = "#{ooc_room.id}"')
print(f'   DEFAULT_HOME = "#{ooc_room.id}"')
print("2. In-game, run:")
print(f"   @typeclass/force #{ooc_room.id} = typeclasses.rooms.OOCRoom")
print("3. Reload server")
print("=" * 70 + "\n")
