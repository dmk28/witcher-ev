"""
Novigrad City Builder
Creates a 40x40 grid map of Novigrad - The largest Free City in the Northern Kingdoms

City Layout:
- Temple District (central, Hierarch's seat of power) - GOLD
- Gildorf (northeast, wealthy merchant quarter) - CYAN
- The Bits (northwest, slums and poverty) - RED
- Harborside (south, massive port and docks) - BLUE
- Glory Lane (east, entertainment district) - MAGENTA
- Putrid Grove (west, cemetery and undertakers) - BLACK
- Oxenfurt Gate District (southwest approach) - GREEN
- Tretogor Gate District (northwest approach) - YELLOW

Surroundings:
- Northern Swamps (dangerous wetlands)
- Western Forests (trade routes to Oxenfurt)
- Eastern Coastline (ocean trade)
- Southern Bay (natural harbor)
"""

import os
import sys
import django

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()

from evennia.objects.models import ObjectDB
from evennia.utils.create import create_object
from typeclasses.rooms import Room
from typeclasses.exits import Exit

# Grid dimensions - Novigrad is larger than Vengerberg
GRID_SIZE = 40

# Color codes for neighborhood identification
DISTRICT_COLORS = {
    'temple_district': '|y',      # Yellow/Gold
    'gildorf': '|c',               # Cyan
    'the_bits': '|r',              # Red
    'harborside': '|b',            # Blue
    'glory_lane': '|m',            # Magenta
    'putrid_grove': '|x',          # Black/Dark
    'oxenfurt_gate': '|g',         # Green
    'tretogor_gate': '|Y',         # Bright Yellow
}

# Area definitions (row_start, row_end, col_start, col_end)
AREAS = {
    'northern_swamps': (0, 7, 0, 39),
    'tretogor_gate': (8, 12, 0, 10),
    'the_bits': (8, 18, 11, 20),
    'putrid_grove': (13, 22, 0, 10),

    # City core
    'temple_district': (13, 22, 21, 30),  # Central, Hierarch's domain
    'gildorf': (8, 17, 31, 39),           # Wealthy northeast
    'glory_lane': (18, 27, 31, 39),       # Entertainment east

    # Southern areas
    'oxenfurt_gate': (23, 27, 0, 15),
    'harborside': (28, 39, 0, 39),        # Massive southern port

    # Wilderness
    'western_forests': (8, 27, 0, 4),     # West edge
    'eastern_coast': (8, 27, 36, 39),     # East edge (ocean)
}

# Room type descriptions with color coding
ROOM_DESCRIPTIONS = {
    'northern_swamps': {
        'name': 'Northern Swamps',
        'color': '|g',
        'desc': 'Thick mist hangs over stagnant pools of murky water. Twisted trees grow at odd angles from the boggy ground, their roots disappearing into the fetid muck.%r%rThe air is thick with moisture and the smell of decay. Strange sounds echo through the fog.',
        'variations': [
            'Mosquitoes swarm in thick clouds, making the air almost unbreathable.',
            'A will-o-wisp dances across the water, its ghostly light luring the unwary.',
            'Rotting logs provide precarious paths across deeper water.',
            'Bones protrude from the mud - whether human or animal is unclear.',
            'The ground squelches underfoot, threatening to swallow boots with each step.',
        ]
    },

    'temple_district': {
        'name': 'Temple District',
        'color': '|y',
        'desc': '|yThe Temple District is the beating heart of Novigrad, where the Eternal Fire\'s influence is absolute. Temples, chapels, and shrines dominate every street corner.%r%rTemple Guards in their distinctive armor patrol constantly, their eyes searching for heretics and non-believers. The smell of incense mingles with the ever-present smoke from ceremonial braziers.|n',
        'variations': [
            'The Hierarch\'s Palace dominates the skyline, its golden spires catching the sunlight.',
            'A street preacher denounces magic and non-humans to a gathered crowd.',
            'Temple Guards march in formation, their footsteps echoing off stone buildings.',
            'Pilgrims prostrate themselves before a shrine to the Eternal Fire.',
            'A public penance is underway, the penitent crawling on bloodied knees.',
            'Bells from a dozen temples ring out, calling the faithful to prayer.',
            'Inquisitors question a trembling merchant about his business dealings.',
            'Collection boxes overflow with coin donated by the fearful faithful.',
        ]
    },

    'gildorf': {
        'name': 'Gildorf',
        'color': '|c',
        'desc': '|cGildorf is where Novigrad\'s wealthiest merchants and most successful traders reside. Elegant townhouses line spotless cobbled streets.%r%rPrivate guards protect gated estates. The air smells of expensive perfumes and fresh flowers. This is wealth and power, merchant-style.|n',
        'variations': [
            'A magnificent mansion boasts a fountain with imported marble statuary.',
            'Liveried servants hurry about their masters\' business.',
            'An expensive carriage rattles past, curtains drawn against common gazes.',
            'A private auction house displays rare goods to wealthy bidders only.',
            'Topiary gardens are sculpted into fantastical shapes.',
            'A moneychanger\'s office deals in currency from across the known world.',
            'Guards in polished armor stand at attention before a merchant lord\'s gate.',
            'The street is swept clean hourly - no refuse mars the perfect cobblestones.',
        ]
    },

    'the_bits': {
        'name': 'The Bits',
        'color': '|r',
        'desc': '|rThe Bits is Novigrad\'s shame - a sprawling slum where the poor, desperate, and forgotten scrape by.%r%rRamshackle buildings lean against each other for support. The stench of human waste, cheap alcohol, and despair fills the air. Violence is common, law enforcement rare.|n',
        'variations': [
            'Beggars huddle in doorways, hands outstretched for any coin.',
            'Children with hollow eyes watch from the shadows, fingers ready to snatch.',
            'A drunk lies unconscious in the gutter, stripped of anything valuable.',
            'Laundry hangs between buildings, gray and tattered.',
            'A makeshift shrine offers hope to those with nothing else.',
            'Rats scurry boldly in broad daylight, fat from abundant refuse.',
            'A street gang marks its territory with crude symbols.',
            'The sound of a fight echoes from a nearby alley - no one intervenes.',
        ]
    },

    'harborside': {
        'name': 'Harborside',
        'color': '|b',
        'desc': '|bHarborside is the commercial engine of Novigrad. The massive port handles ships from across the world.%r%rDozens of piers extend into the bay. Warehouses store goods worth kingdoms. The air smells of salt water, tar, fish, and exotic spices from distant lands.|n',
        'variations': [
            'A massive galleon is being unloaded, exotic cargo swinging from cranes.',
            'Longshoremen haul crates while overseers shout instructions.',
            'Sailors from Skellige brawl with Nilfgaardian merchants outside a tavern.',
            'Fish markets display the morning\'s catch on ice-covered tables.',
            'A customs house inspector examines cargo manifests suspiciously.',
            'Smugglers\' row - where goods enter the city without official notice.',
            'Ship repairers work on a vessel in dry dock.',
            'The harbormaster\'s office overlooks the entire port operation.',
        ]
    },

    'glory_lane': {
        'name': 'Glory Lane',
        'color': '|m',
        'desc': '|mGlory Lane is Novigrad\'s entertainment district - a place of pleasure, vice, and forbidden delights.%r%rBrothels, gambling dens, and taverns line the streets. Musicians play for coin. The area comes alive at night, when the respectable citizens pretend it doesn\'t exist.|n',
        'variations': [
            'A brothel madam calls to passersby, advertising her establishment\'s offerings.',
            'Dice clatter in a gambling den, fortunes won and lost on each throw.',
            'Street musicians play popular songs for a growing crowd.',
            'A fight breaks out between drunk patrons outside a tavern.',
            'Perfumed courtesans parade in expensive silks and jewels.',
            'The King of Beggars\' spies watch everything, reporting to their master.',
            'A discrete entrance leads to an opium den.',
            'Temple Guards raid a suspected witch\'s fortune-telling parlor.',
        ]
    },

    'putrid_grove': {
        'name': 'Putrid Grove',
        'color': '|x',
        'desc': '|xPutrid Grove is Novigrad\'s cemetery district and the domain of undertakers.%r%rGraveyards stretch in all directions, headstones crowding ancient burial grounds. The living who work here - undertakers, gravediggers, and corpse-handlers - are viewed with suspicion and fear.|n',
        'variations': [
            'An undertaker measures a fresh corpse for a coffin.',
            'Gravediggers work by torchlight, always behind on their grim task.',
            'A family mourns at a fresh grave, ignoring the stench of older burials.',
            'Ghouls have been spotted at night - guards patrol the cemetery walls.',
            'A mausoleum bears the crest of a once-great family now forgotten.',
            'Crows circle overhead, their cawing the only sound.',
            'A grave robber\'s tools lie abandoned - their owner fled from something.',
            'The Eternal Fire temple maintains a section for condemned heretics.',
        ]
    },

    'oxenfurt_gate': {
        'name': 'Oxenfurt Gate District',
        'color': '|g',
        'desc': '|gThe Oxenfurt Gate District serves travelers from the famous university city.%r%rInns cater to scholars and students. Bookshops sell rare texts. The atmosphere is more intellectual than other districts, though the Temple Guards still watch for heresy.|n',
        'variations': [
            'Students from Oxenfurt Academy debate philosophy loudly over wine.',
            'A bookseller displays rare manuscripts in a protected case.',
            'Scholars hire scribes to copy important texts.',
            'An inn advertises rooms "suitable for scholarly pursuits."',
            'A glassblower creates scientific instruments for university trade.',
        ]
    },

    'tretogor_gate': {
        'name': 'Tretogor Gate District',
        'color': '|Y',
        'desc': '|YThe Tretogor Gate District handles trade from Redania\'s capital.%r%rMerchant caravans arrive regularly. The district has a military feel despite Novigrad\'s free city status - Redanian influence is strong here.|n',
        'variations': [
            'A Redanian trade caravan arrives, guards watching for bandits.',
            'Merchants negotiate trade agreements in a guild house.',
            'Soldiers from Tretogor drink in a tavern, technically on leave.',
            'A customs checkpoint inspects all cargo entering from the north.',
        ]
    },

    'western_forests': {
        'name': 'Western Forest Trails',
        'color': '|g',
        'desc': 'Forest trails lead west toward Oxenfurt and beyond. The woods are well-traveled but not entirely safe.%r%rTraders prefer to travel in groups.',
        'variations': [
            'A merchant caravan makes camp for the night.',
            'Bandits are rumored to operate from these woods.',
            'A forest shrine marks the boundary of Novigrad\'s influence.',
        ]
    },

    'eastern_coast': {
        'name': 'Eastern Coastline',
        'color': '|b',
        'desc': 'The eastern coast where the city meets the ocean. Waves crash against rocky shores.%r%rSeagulls cry overhead, and the salt spray is constant.',
        'variations': [
            'A lighthouse warns ships of dangerous rocks.',
            'Fishermen haul in nets full of the morning catch.',
            'Tide pools reveal strange sea creatures.',
        ]
    },
}

# Special locations (specific coordinates get unique rooms)
SPECIAL_LOCATIONS = {
    # Temple District
    (17, 25): {
        'name': '|yHierarch Square|n',
        'desc': '|yThe Hierarch Square is the absolute center of power in Novigrad. The Hierarch\'s Palace dominates the plaza, its golden domes visible from everywhere in the city.%r%rTemple Guards stand at rigid attention every few paces. Massive statues depict the prophets of the Eternal Fire. Public punishments and burnings occur here - a reminder of the Church\'s authority.|n',
        'color': '|y',
    },

    (18, 26): {
        'name': '|yTemple of the Eternal Fire|n',
        'desc': '|yThe Great Temple of the Eternal Fire is a massive cathedral, its architecture designed to inspire awe and obedience.%r%rThe Eternal Flame burns in a great brazier, never extinguished. Priests conduct constant services. The walls are decorated with scenes of divine judgment - the faithful ascending, heretics burning.|n',
        'color': '|y',
    },

    # Gildorf
    (12, 35): {
        'name': '|cVivaldi Bank|n',
        'desc': '|cVivaldi Bank is the most prestigious financial institution in the North. The building is fortress-like - security is paramount.%r%rInside, clerks manage accounts worth more than small kingdoms. The Vivaldi family\'s dwarf heritage shows in the meticulous record-keeping and honest dealings. Only the wealthy are welcomed.|n',
        'color': '|c',
    },

    (13, 36): {
        'name': '|cGildorf Auction House|n',
        'desc': '|cThe Gildorf Auction House deals in rare and valuable goods. Art, jewels, magical items (discreetly), and antiquities change hands here.%r%rBidding is intense, fortunes made and lost. The auction house takes a healthy percentage of every sale.|n',
        'color': '|c',
    },

    # The Bits
    (14, 15): {
        'name': '|rThe Kingfisher Inn|n',
        'desc': '|rThe Kingfisher is one of The Bits\' better establishments, though that\'s not saying much.%r%rThe common room is crowded with laborers, beggars, and those who can\'t afford better. The ale is watered down but cheap. Upstairs rooms are available for a few coppers - bed bugs included free of charge.|n',
        'color': '|r',
    },

    (15, 16): {
        'name': '|rKing of Beggars\' Hideout|n',
        'desc': '|rThis unassuming building is actually the headquarters of the King of Beggars, Novigrad\'s underworld ruler.%r%rFrom here, he controls beggars, thieves, and spies throughout the city. His network knows everything that happens in Novigrad. Gaining audience requires connections and coin.|n',
        'color': '|r',
    },

    # Harborside
    (33, 20): {
        'name': '|bHarbormaster\'s Tower|n',
        'desc': '|bThe Harbormaster\'s Tower overlooks the entire port. From here, every ship entering and leaving is tracked.%r%rTariffs are collected, manifests examined, smugglers caught (sometimes). The harbormaster wields enormous economic power - his blessing or curse can make or break merchant ventures.|n',
        'color': '|b',
    },

    (34, 18): {
        'name': '|bThe Golden Sturgeon Tavern|n',
        'desc': '|bThe Golden Sturgeon is Harborside\'s most famous tavern. Sailors, merchants, and smugglers all drink here.%r%rThe food is excellent - fresh fish prepared by a talented cook. Upstairs rooms are clean and secure. Information flows as freely as the ale, for those who know how to listen.|n',
        'color': '|b',
    },

    # Glory Lane
    (22, 35): {
        'name': '|mThe Passiflora|n',
        'desc': '|mThe Passiflora is Novigrad\'s most exclusive and expensive brothel. Only the wealthy can afford its pleasures.%r%rElegantly decorated, it rivals noble estates. The courtesans are beautiful, educated, and discrete. Many important deals are made here - the Passiflora\'s madam knows all Novigrad\'s secrets.|n',
        'color': '|m',
    },

    (23, 34): {
        'name': '|mRosemary and Thyme Cabaret|n',
        'desc': '|mThe Rosemary and Thyme is a cabaret and inn catering to artists, bards, and those seeking entertainment.%r%rPerformances occur nightly - music, poetry, theatrical productions. The atmosphere is bohemian, a contrast to Novigrad\'s usual religious severity. Temple Guards watch it suspiciously.|n',
        'color': '|m',
    },

    # Putrid Grove
    (18, 5): {
        'name': '|xEternal Fire Cemetery - Main Gate|n',
        'desc': '|xThe main cemetery gate is flanked by statues of skeletal angels. Beyond, thousands of graves stretch into the mist.%r%rUndertakers'' wagons arrive regularly with fresh corpses. Gravediggers work endlessly - Novigrad\'s size means death is a booming business. Necrophages are an ever-present threat.|n',
        'color': '|x',
    },

    # Gates
    (27, 10): {
        'name': '|gOxenfurt Gate|n',
        'desc': '|gThe Oxenfurt Gate is the main western entrance to Novigrad. Massive wooden doors reinforced with iron can seal the city.%r%rGuards check everyone entering, looking for smuggled goods and wanted criminals. A steady stream of scholars and merchants passes through daily.|n',
        'color': '|g',
    },

    (10, 5): {
        'name': '|YTretogor Gate|n',
        'desc': '|YThe Tretogor Gate handles trade from Redania\'s capital. Despite Novigrad\'s free city status, Redanian influence is strong here.%r%rCustoms inspectors are thorough - Redanian spies work to ensure nothing threatens their interests. Soldiers from Tretogor often "visit" the gate area.|n',
        'color': '|Y',
    },

    # Connection to Vengerberg (staff-locked)
    (15, 0): {
        'name': '|gAncient Waystone|n',
        'desc': '|gAn ancient waystone stands here, covered in runes of power. Magical energy emanates from the standing stone.%r%r%r|y[STAFF ONLY]: This waystone connects to other major cities via teleportation magic. Only those with proper authorization can activate it.|n',
        'color': '|g',
    },
}


def get_area_type(row, col):
    """Determine which area a coordinate belongs to."""
    for area_name, (r_start, r_end, c_start, c_end) in AREAS.items():
        if r_start <= row <= r_end and c_start <= col <= c_end:
            return area_name
    return 'wilderness'


def get_room_data(row, col, area_type):
    """Generate room name and description based on location."""
    # Check for special locations first
    if (row, col) in SPECIAL_LOCATIONS:
        return SPECIAL_LOCATIONS[(row, col)]

    # Get template for this area type
    template = ROOM_DESCRIPTIONS.get(area_type)
    if not template:
        return {
            'name': f'Wilderness ({row}, {col})',
            'desc': 'An unremarkable location.',
            'color': '|n',
        }

    # Use row/col as seed for variation selection
    if template.get('variations'):
        variation_idx = (row * col) % len(template['variations'])
        variation = template['variations'][variation_idx]
        full_desc = f"{template['desc']}%r%r{variation}"
    else:
        full_desc = template['desc']

    # Generate unique room name
    area_name = template['name']
    color = template.get('color', '|n')

    # City districts get street names
    if area_type in ['temple_district', 'gildorf', 'the_bits', 'harborside', 'glory_lane', 'putrid_grove']:
        street_names = {
            'temple_district': ['Hierarch\'s Way', 'Sanctified Street', 'Prophet Avenue', 'Penance Lane', 'Devotion Road'],
            'gildorf': ['Gold Street', 'Merchant\'s Boulevard', 'Prosperity Lane', 'Commerce Avenue', 'Wealth Way'],
            'the_bits': ['Broken Street', 'Beggar\'s Row', 'Misery Lane', 'Slum Alley', 'Poverty Road'],
            'harborside': ['Anchor Street', 'Harbor Road', 'Wharf Lane', 'Pier Avenue', 'Dockside Way'],
            'glory_lane': ['Pleasure Street', 'Vice Lane', 'Entertainment Row', 'Sin Alley', 'Indulgence Avenue'],
            'putrid_grove': ['Burial Street', 'Undertaker\'s Row', 'Mourning Lane', 'Grave Road', 'Corpse Alley'],
        }

        if area_type in street_names:
            street_idx = (row + col) % len(street_names[area_type])
            street = street_names[area_type][street_idx]
            return {
                'name': f'{color}{street}, {area_name}|n',
                'desc': full_desc,
                'color': color,
            }

    return {
        'name': f'{color}{area_name} ({row},{col})|n',
        'desc': full_desc,
        'color': color,
    }


def create_room_grid():
    """Create all rooms in a 40x40 grid."""
    print(f"Creating {GRID_SIZE}x{GRID_SIZE} room grid for Novigrad...")
    print(f"Total rooms to create: {GRID_SIZE * GRID_SIZE}")

    rooms = {}
    created_count = 0

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            area_type = get_area_type(row, col)
            room_data = get_room_data(row, col, area_type)

            # Create room
            room_key = f"novigrad_{row}_{col}"

            # Check if room already exists
            existing = ObjectDB.objects.filter(db_key=room_key).first()
            if existing:
                rooms[(row, col)] = existing
                continue

            room = create_object(
                Room,
                key=room_key,
                location=None,
                home=None,
            )

            # Set room properties
            room.db.desc = room_data['desc']
            room.db.display_name = room_data['name']
            room.db.area = area_type
            room.db.coordinates = (row, col)
            room.db.color = room_data.get('color', '|n')
            room.db.city = 'novigrad'

            rooms[(row, col)] = room
            created_count += 1

            if created_count % 100 == 0:
                print(f"Created {created_count} rooms...")

    print(f"Finished creating {created_count} new rooms!")
    return rooms


def connect_rooms(rooms):
    """Create exits connecting all rooms in cardinal directions."""
    print("Connecting Novigrad rooms with exits...")

    exit_count = 0

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            room = rooms.get((row, col))
            if not room:
                continue

            # North
            if row > 0:
                north_room = rooms.get((row - 1, col))
                if north_room:
                    create_object(Exit, key='north', location=room, destination=north_room)
                    create_object(Exit, key='south', location=north_room, destination=room)
                    exit_count += 2

            # East
            if col < GRID_SIZE - 1:
                east_room = rooms.get((row, col + 1))
                if east_room:
                    create_object(Exit, key='east', location=room, destination=east_room)
                    create_object(Exit, key='west', location=east_room, destination=room)
                    exit_count += 2

            if exit_count % 1000 == 0:
                print(f"Created {exit_count} exits...")

    print(f"Finished creating {exit_count} exits!")


def create_city_connection():
    """Create magical connection between Novigrad and Vengerberg (staff-locked)."""
    print("Creating inter-city connection...")

    # Find Novigrad waystone (15, 0)
    novigrad_waystone = ObjectDB.objects.filter(db_key="novigrad_15_0").first()

    # Find Vengerberg connection point (we'll use the northern gate area)
    vengerberg_waystone = ObjectDB.objects.filter(db_key="vengerberg_10_0").first()

    if not vengerberg_waystone:
        print("Creating Vengerberg waystone...")
        vengerberg_waystone = create_object(
            Room,
            key="vengerberg_waystone",
            location=None,
            home=None,
        )
        vengerberg_waystone.db.desc = (
            "|gAn ancient waystone stands in a clearing north of Vengerberg. "
            "Runes of power cover the standing stone, glowing faintly with magical energy.%r%r"
            "%r|y[STAFF ONLY]: This waystone connects to Novigrad via teleportation magic. "
            "Only those with proper authorization can activate it.|n"
        )
        vengerberg_waystone.db.display_name = "|gAncient Waystone (Vengerberg)|n"
        vengerberg_waystone.db.area = "waystone"
        vengerberg_waystone.db.city = "vengerberg"

    if novigrad_waystone and vengerberg_waystone:
        # Create staff-locked exits
        # From Novigrad to Vengerberg
        nov_to_ven = create_object(
            Exit,
            key='activate waystone to vengerberg',
            aliases=['vengerberg', 'to vengerberg'],
            location=novigrad_waystone,
            destination=vengerberg_waystone
        )
        nov_to_ven.locks.add("traverse:perm(Builder)")

        # From Vengerberg to Novigrad
        ven_to_nov = create_object(
            Exit,
            key='activate waystone to novigrad',
            aliases=['novigrad', 'to novigrad'],
            location=vengerberg_waystone,
            destination=novigrad_waystone
        )
        ven_to_nov.locks.add("traverse:perm(Builder)")

        print(f"Created staff-locked connection:")
        print(f"  Novigrad Waystone (#{novigrad_waystone.id}) <-> Vengerberg Waystone (#{vengerberg_waystone.id})")
    else:
        print("Warning: Could not create city connection - waystones not found")


def set_default_home():
    """Set recommendation for default home location."""
    print("Identifying recommended home location...")

    # Find Hierarch Square (17, 25) - central location
    hierarch_square = ObjectDB.objects.filter(db_key="novigrad_17_25").first()
    if hierarch_square:
        print(f"Recommended default home: {hierarch_square.db.display_name}")
        print(f"Room ID: #{hierarch_square.id}")
    else:
        print("Warning: Hierarch Square not found!")


def main():
    """Main builder function."""
    print("=" * 70)
    print("NOVIGRAD CITY BUILDER")
    print("The Free City - Largest in the Northern Kingdoms")
    print("=" * 70)
    print()

    # Create all rooms
    rooms = create_room_grid()

    print()

    # Connect rooms with exits
    connect_rooms(rooms)

    print()

    # Create connection to Vengerberg
    create_city_connection()

    print()

    # Set default home
    set_default_home()

    print()
    print("=" * 70)
    print("NOVIGRAD BUILD COMPLETE!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  Total rooms: {len(rooms)}")
    print(f"  Grid size: {GRID_SIZE}x{GRID_SIZE}")
    print()
    print("Districts (Color-Coded):")
    print("  |yTemple District|n - Hierarch's domain (GOLD)")
    print("  |cGildorf|n - Wealthy merchants (CYAN)")
    print("  |rThe Bits|n - Slums and poverty (RED)")
    print("  |bHarborside|n - Massive port (BLUE)")
    print("  |mGlory Lane|n - Entertainment district (MAGENTA)")
    print("  |xPutrid Grove|n - Cemeteries (BLACK)")
    print("  |gOxenfurt Gate|n - Western approach (GREEN)")
    print("  |YTretogor Gate|n - Northern approach (BRIGHT YELLOW)")
    print()
    print("Key Locations:")
    print("  Hierarch Square: (17, 25)")
    print("  Eternal Fire Temple: (18, 26)")
    print("  Vivaldi Bank: (12, 35)")
    print("  The Passiflora: (22, 35)")
    print("  Harbormaster's Tower: (33, 20)")
    print("  King of Beggars' Hideout: (15, 16)")
    print("  Novigrad Waystone: (15, 0) [STAFF-LOCKED TO VENGERBERG]")
    print()


if __name__ == '__main__':
    main()
