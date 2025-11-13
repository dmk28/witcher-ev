"""
Fix GameMaster account and create OOC room.
Run in-game with: @py exec(open('world/fix_gamemaster.py').read())
"""

from evennia.utils.create import create_object
from evennia.objects.models import ObjectDB
from evennia.accounts.models import AccountDB
from typeclasses.rooms import OOCRoom
from typeclasses.characters import WitcherCharacter as WitcherCharacterTypeclass
from world.witcher_rpg.models import WitcherCharacter, CharacterStats, CharacterSkills, Vocation, Country

print("\n" + "=" * 70)
print("FIXING GAMEMASTER AND CREATING OOC ROOM")
print("=" * 70 + "\n")

# Step 1: Get GameMaster account
try:
    gm = AccountDB.objects.get(username='GameMaster')
    print(f"✓ Found GameMaster account (#{gm.id})")
except AccountDB.DoesNotExist:
    print("✗ GameMaster account not found!")
    gm = None

# Step 2: Unpuppet from Limbo if needed
if gm:
    try:
        gm.unpuppet_all()
        print("✓ Unpuppeted GameMaster from all objects")
    except (AttributeError, TypeError):
        print("✓ Skipping unpuppet (no active sessions)")

# Step 3: Create OOC Room
existing_ooc = ObjectDB.objects.filter(db_key="OOC Lobby", db_typeclass_path="typeclasses.rooms.OOCRoom").first()
if existing_ooc:
    ooc_room = existing_ooc
    print(f"✓ OOC Lobby already exists (#{ooc_room.id})")
else:
    ooc_room = create_object(
        OOCRoom,
        key="OOC Lobby",
        location=None,
    )
    print(f"✓ Created OOC Lobby (#{ooc_room.id})")

# Step 4: Get starting location for character
try:
    start_location = ObjectDB.objects.get(id=595)  # Vengerberg Central Market Square
    print(f"✓ Using starting location: {start_location.key} (#{start_location.id})")
except ObjectDB.DoesNotExist:
    start_location = ObjectDB.objects.get(id=2)  # Limbo fallback
    print(f"✓ Using fallback location: {start_location.key} (#{start_location.id})")

# Step 5: Check if GameMaster already has a character
if gm:
    existing_chars = list(gm.characters)
    if existing_chars:
        char = existing_chars[0]
        print(f"✓ GameMaster already has character: {char.key} (#{char.id})")
    else:
        # Step 6: Create a basic character for GameMaster
        try:
            # Create character object
            char = create_object(
                WitcherCharacterTypeclass,
                key="GameMaster",
                location=start_location,
                home=start_location,
            )

            # Create basic stats
            stats = CharacterStats.objects.create(
                strength=5, agility=5, endurance=5, reflexes=5,
                wit=5, intelligence=5, willpower=5, perception=5,
                charm=5, appearance=5, graces=5, cunning=5
            )

            # Create basic skills
            skills = CharacterSkills.objects.create(
                blades=5, crafting_type='none', crafting_skill=0
            )

            # Get a default vocation (soldier)
            vocation = Vocation.objects.filter(name='soldier').first()
            if not vocation:
                vocation = Vocation.objects.first()

            # Create WitcherCharacter record
            witcher_char = WitcherCharacter.objects.create(
                db_object=char,
                character_name="GameMaster",
                vocation=vocation,
                stats=stats,
                skills=skills,
                background="Game Master character",
                physical_description="An ethereal presence.",
                race='human',
                social_rank=5,
            )

            # Link to account
            gm.characters.add(char)
            char.db.account = gm

            print(f"✓ Created GameMaster character (#{char.id})")

            # Give Developer permissions
            char.permissions.add('Developer')
            print("✓ Added Developer permissions")

        except Exception as e:
            print(f"✗ Error creating character: {e}")
            import traceback
            traceback.print_exc()

print("\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)
print(f"OOC Lobby: #{ooc_room.id}")
print(f"\nTo complete setup, add to server/conf/settings.py:")
print(f'START_LOCATION = "#{ooc_room.id}"')
print(f'DEFAULT_HOME = "#{ooc_room.id}"')
print("\nThen run: evennia reload")
print("=" * 70 + "\n")
