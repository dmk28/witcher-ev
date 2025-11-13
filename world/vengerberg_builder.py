"""
Vengerberg City Builder
Creates a 32x32 grid map of Vengerberg and surrounding areas.

City Layout:
- Temple District (NW city area)
- Royal Quarter (NE city area)
- Market Ward (Central city area)
- Craftsmen Quarter (SW city area)
- River Ward (SE city area, along Pontar River)

Surroundings:
- Northern Woods (wilderness, hunting grounds)
- Western Woods (forest, bandit territory)
- Eastern River (Pontar River with docks)
- Southern Farmlands (agriculture, villages)
- Iron Mine (northwest of city)
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

# Grid dimensions
GRID_SIZE = 32

# Area definitions (row_start, row_end, col_start, col_end)
AREAS = {
    'northern_woods': (0, 5, 0, 31),
    'western_woods': (6, 23, 0, 5),
    'iron_mine': (6, 10, 6, 11),

    # City wards (rows 11-23, cols 8-25)
    'temple_district': (11, 16, 8, 15),
    'royal_quarter': (11, 16, 16, 25),
    'market_ward': (17, 20, 8, 25),
    'craftsmen_quarter': (21, 23, 8, 16),
    'river_ward': (21, 23, 17, 25),

    # City outskirts
    'northern_approach': (6, 10, 12, 25),
    'western_approach': (11, 23, 6, 7),
    'eastern_river': (6, 28, 26, 31),
    'southern_farmlands': (24, 31, 0, 25),
    'southern_river': (29, 31, 26, 31),
}

# Room type descriptions
ROOM_DESCRIPTIONS = {
    'northern_woods': {
        'name': 'Northern Woods',
        'desc': 'Dense forest stretches in all directions. Ancient oaks and pines tower overhead, their branches creating a canopy that filters the sunlight. The air is thick with the scent of moss and pine needles.%r%rAnimal tracks crisscross the forest floor.',
        'variations': [
            'A small clearing opens up, revealing a circle of mushrooms growing in a perfect ring.',
            'Thick undergrowth makes progress difficult. Thorny bushes catch at clothing.',
            'The trees thin slightly here, allowing more light to penetrate the canopy.',
            'A fallen log, covered in moss and fungi, blocks part of the path.',
            'The sound of birds echoes through the trees, along with the occasional rustle of small animals.',
        ]
    },

    'western_woods': {
        'name': 'Western Woods',
        'desc': 'The western forest is darker and more ominous than the northern woods. Twisted trees lean at odd angles, and the undergrowth is sparse.%r%rThese woods are known to harbor bandits and worse.',
        'variations': [
            'A crude campsite shows signs of recent use - probably bandits.',
            'The path here is barely visible, overgrown and neglected.',
            'Something large has passed through here recently, breaking branches.',
            'An old tree bears knife marks - possibly trail blazing or territorial markers.',
            'The forest is unnaturally quiet here. Too quiet.',
        ]
    },

    'iron_mine': {
        'name': 'Iron Mine',
        'desc': 'The entrance to an iron mine cuts into the hillside. Wooden supports frame the opening, and the ground is stained with rust-colored ore dust.%r%rThe sound of pickaxes echoes from within.',
        'variations': [
            'Miners emerge from the darkness, faces covered in dust and sweat.',
            'Mine carts sit on rails, waiting to be filled with ore.',
            'A foreman oversees workers hauling ore from the mine entrance.',
            'The smell of sulfur and metal hangs heavy in the air.',
            'Piles of extracted ore are sorted and prepared for transport.',
        ]
    },

    'temple_district': {
        'name': 'Temple District',
        'desc': 'The Temple District is the spiritual heart of Vengerberg. Stone temples and shrines dedicated to various deities line the streets.%r%rThe air here carries the scent of incense and prayers can be heard at all hours.',
        'variations': [
            'The Great Temple dominates this area, its spires reaching toward the heavens.',
            'Priests in ceremonial robes walk these streets, blessing passersby.',
            'A small shrine to Melitele is tended by a young acolyte.',
            'Pilgrims gather in a plaza, seeking blessings and divine guidance.',
            'Sacred gardens are maintained with meticulous care, offering places for contemplation.',
            'A monastery stands behind iron gates, its inhabitants devoted to silent prayer.',
            'Temple bells ring the hours, their sound carrying across the district.',
            'Donation boxes near shrines overflow with offerings from the faithful.',
        ]
    },

    'royal_quarter': {
        'name': 'Royal Quarter',
        'desc': 'The Royal Quarter is where Vengerberg\'s nobility reside. Grand estates with manicured gardens line wide, clean streets.%r%rArmed guards watch from every corner, ensuring the safety of the city\'s elite.',
        'variations': [
            'A magnificent palace rises above the other buildings, flying the colors of Aedirn.',
            'Noble ladies in fine silks stroll through a private park, attended by servants.',
            'An imposing manor house is fronted by a courtyard with a magnificent fountain.',
            'Guards in polished armor stand at attention before a noble\'s residence.',
            'A garden party is underway in a visible estate, nobles laughing over wine.',
            'Expensive carriages wait outside an estate, horses stamping impatiently.',
            'The street is immaculately clean, with servants sweeping away any debris.',
            'A noble\'s herald announces arrivals at a grand estate entrance.',
        ]
    },

    'market_ward': {
        'name': 'Market Ward',
        'desc': 'The Market Ward is the bustling heart of Vengerberg\'s commerce. Stalls and shops line every street, merchants hawking their wares.%r%rThe air is filled with shouting vendors, the smell of food, and the constant press of crowds.',
        'variations': [
            'The central marketplace is a maze of stalls selling everything imaginable.',
            'A weaponsmith\'s shop displays swords and armor in the window.',
            'The smell of fresh bread wafts from a baker\'s shop.',
            'Street performers entertain crowds while children pick pockets.',
            'A tavern called "The Prancing Pony" does brisk business.',
            'Merchants argue loudly over prices while customers watch with amusement.',
            'An apothecary shop advertises potions and herbs with hand-painted signs.',
            'Food vendors sell hot meals from carts, the aromas mingling.',
            'A town crier announces news from the palace steps.',
            'Pickpockets work the crowds while guards try to maintain order.',
        ]
    },

    'craftsmen_quarter': {
        'name': 'Craftsmen Quarter',
        'desc': 'The Craftsmen Quarter rings with the sounds of industry. Forges, workshops, and artisan studios fill every building.%r%rThe smell of hot metal, fresh-cut wood, and tanning leather permeates the air.',
        'variations': [
            'A blacksmith\'s forge glows red-hot, the smith hammering steel rhythmically.',
            'A leatherworker\'s shop displays belts, boots, and armor pieces.',
            'The sound of sawing comes from a carpenter\'s workshop.',
            'An armorsmith fits a knight with a custom breastplate.',
            'Apprentices hurry through the streets carrying materials for their masters.',
            'A jeweler carefully sets gems into a golden necklace.',
            'The tanners\' area reeks of chemicals used to treat hides.',
            'A fletcher crafts arrows with practiced efficiency.',
        ]
    },

    'river_ward': {
        'name': 'River Ward',
        'desc': 'The River Ward sits along the banks of the Pontar River. Docks extend into the water, and warehouses store goods from river trade.%r%rFishermen mend nets while longshoremen load and unload barges.',
        'variations': [
            'Docks bustle with activity as ships load and unload cargo.',
            'The smell of fish is overwhelming near the market stalls.',
            'Sailors from distant lands swap stories in a waterfront tavern.',
            'A warehouse bears the mark of the Merchants\' Guild.',
            'Fishermen haul in their catch, seagulls crying overhead.',
            'A harbormaster\'s office oversees the river traffic.',
            'Children play on the docks, diving for coins thrown by amused sailors.',
            'River barges are moored along the quay, rocking gently.',
        ]
    },

    'northern_approach': {
        'name': 'Northern Approach',
        'desc': 'The northern approach to Vengerberg is well-traveled. The road is wide and maintained, showing the importance of the city.%r%rTravelers and merchants frequent this route.',
        'variations': [
            'A roadside inn offers rest to weary travelers.',
            'Guards patrol the road, keeping it safe from bandits.',
            'Merchants\' wagons trundle past, headed for the city markets.',
            'A milestone marks the distance to Vengerberg\'s gates.',
        ]
    },

    'western_approach': {
        'name': 'Western Approach',
        'desc': 'The western approach is less traveled than the northern road. The path here skirts the edge of dangerous woods.%r%rVigilance is advised.',
        'variations': [
            'A warning post cautions travelers about bandits in the nearby woods.',
            'The road here is in poor repair, with deep ruts and potholes.',
        ]
    },

    'eastern_river': {
        'name': 'Pontar River',
        'desc': 'The mighty Pontar River flows swift and deep. Its waters are the lifeblood of trade and commerce for Vengerberg.%r%rFishing boats and trade barges navigate the current.',
        'variations': [
            'The river is wide here, the far bank barely visible through morning mist.',
            'Strong currents swirl and eddy, making swimming dangerous.',
            'A small fishing boat is moored to the bank.',
            'The water is surprisingly clear, fish visible in the shallows.',
            'Reeds and rushes grow thick along the riverbank.',
        ]
    },

    'southern_farmlands': {
        'name': 'Southern Farmlands',
        'desc': 'Fertile farmlands stretch south of Vengerberg. Fields of wheat and barley wave in the breeze.%r%rSmall farming villages dot the landscape.',
        'variations': [
            'A farmer plows his field with a pair of oxen.',
            'A small farmhouse sits amid golden wheat fields.',
            'Children play in an irrigation ditch while their parents work.',
            'A windmill turns slowly, grinding grain into flour.',
            'Sheep graze in a fenced pasture, watched by a shepherd.',
            'A small village green hosts a weekly market.',
        ]
    },

    'southern_river': {
        'name': 'Southern Riverbank',
        'desc': 'The Pontar River continues its journey south. Here it is quieter, away from the bustle of the city docks.%r%rWildlife is abundant along these banks.',
        'variations': [
            'Ducks paddle in the shallows, diving for food.',
            'A beaver dam has created a small pond off the main channel.',
            'Willows drape their branches into the water.',
        ]
    },
}

# Special locations (specific coordinates get unique rooms)
SPECIAL_LOCATIONS = {
    # City Gates
    (10, 16): {
        'name': 'Northern Gate of Vengerberg',
        'desc': 'The Northern Gate stands tall and imposing, marking the main entrance to Vengerberg. Massive wooden doors reinforced with iron bands can be closed in times of danger. Guards in the livery of Aedirn stand watch, scrutinizing all who enter.%r%rAbove the gate, the city\'s coat of arms is carved in stone. The road beyond leads into the heart of the city.',
    },

    (10, 17): {
        'name': 'Northern Gate Plaza',
        'desc': 'Just inside the Northern Gate, a wide plaza welcomes visitors to Vengerberg. Merchants set up stalls here to catch travelers before they venture deeper into the city.%r%rA large fountain stands at the plaza\'s center, its waters crystal clear.',
    },

    # Temple District - Great Temple
    (13, 11): {
        'name': 'The Great Temple of Melitele',
        'desc': 'The Great Temple of Melitele is the largest and most magnificent religious structure in Vengerberg. White marble columns support a soaring dome, and stained glass windows cast colored light across the interior.%r%rPriestesses in white robes tend to the faithful, offering healing and counsel. The air is thick with incense and the murmur of prayers.',
    },

    # Royal Quarter - Palace
    (13, 21): {
        'name': 'Royal Palace of Vengerberg',
        'desc': 'The Royal Palace is a masterwork of architecture, all soaring spires and elegant stonework. Gardens surround the palace, immaculately maintained by an army of gardeners.%r%rGuards in ceremonial armor stand at every entrance, their halberds gleaming. Only those with official business are permitted to enter.',
    },

    # Market Ward - Central Market
    (18, 16): {
        'name': 'Central Market Square',
        'desc': 'The Central Market Square is the beating heart of Vengerberg\'s economy. Hundreds of stalls crowd the large plaza, merchants selling everything from food to weapons to magical talismans.%r%rThe noise is deafening - vendors shouting, customers haggling, animals protesting. The smell is equally overwhelming: spices, sweat, livestock, and food cooking. A large fountain provides drinking water in the square\'s center.',
    },

    # Craftsmen Quarter - Master Forge
    (22, 12): {
        'name': 'The Master Forge',
        'desc': 'The Master Forge is run by Dwarven smiths, their skill legendary throughout the realm. The heat from the massive forge is intense, the glow of molten metal illuminating the workshop.%r%rWeapons and armor of extraordinary quality hang on display. The master smith himself, a grizzled dwarf named Yarpen, oversees every piece personally.',
    },

    # River Ward - Harbor Master
    (22, 22): {
        'name': 'Harbor Master\'s Office',
        'desc': 'The Harbor Master\'s Office overlooks the main docks. A weathered building of stone and timber, it serves as the administrative center for all river trade.%r%rInside, the harbor master keeps ledgers of every ship, cargo manifest, and toll collected. Maps of the Pontar River cover the walls, marked with hazards and trade routes.',
    },

    # Mine - Main Shaft
    (7, 8): {
        'name': 'Iron Mine - Main Shaft',
        'desc': 'The main shaft of the iron mine descends deep into the earth. Torches light the entrance, but darkness swallows the tunnel within.%r%rMiners trudge in and out, faces blackened with dust. The sound of pickaxes striking stone echoes from below. A foreman checks every worker, ensuring production quotas are met.',
    },

    # Woods - Druid Grove
    (2, 15): {
        'name': 'Hidden Druid Grove',
        'desc': 'A sacred grove hidden deep in the northern woods. Ancient standing stones form a circle, covered in moss and carved with runic symbols.%r%rThe druids who tend this place worship the old gods, far from the temples of the city. The air here feels charged with primal magic.',
    },

    # Taverns
    (18, 14): {
        'name': 'The Prancing Pony Tavern',
        'desc': 'The Prancing Pony is one of Vengerberg\'s most popular taverns. A large common room features a roaring fireplace, rough wooden tables, and a bar that runs the length of the back wall.%r%rThe ale flows freely, and the food is simple but hearty. Travelers, merchants, and locals mix freely here, swapping gossip and stories. A bard plays in the corner, though few pay attention.',
    },

    (22, 19): {
        'name': 'The Rusty Anchor Inn',
        'desc': 'The Rusty Anchor caters to sailors and dock workers. The common room is cramped and smoky, smelling of fish, sweat, and cheap alcohol.%r%rDespite its rough atmosphere, the Anchor is known for having the best fish stew in the city. Sailors from distant ports trade tales of adventure and danger.',
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
        }

    # Use row/col as seed for variation selection
    variation_idx = (row * col) % len(template.get('variations', ['']))

    base_desc = template['desc']
    if template.get('variations'):
        variation = template['variations'][variation_idx]
        full_desc = f"{base_desc}%r%r{variation}"
    else:
        full_desc = base_desc

    # Generate unique room name with coordinates
    area_name = template['name']

    # Add directional flavor for non-city areas
    if area_type in ['northern_woods', 'western_woods', 'eastern_river', 'southern_farmlands']:
        return {
            'name': f'{area_name} ({row},{col})',
            'desc': full_desc,
        }
    else:
        # City areas get more specific names
        street_names = {
            'temple_district': ['Prayer Street', 'Pilgrim Way', 'Temple Avenue', 'Sacred Path', 'Devotion Lane'],
            'royal_quarter': ['Noble Avenue', 'Crown Street', 'Palace Road', 'Aristocrat Way', 'Royal Boulevard'],
            'market_ward': ['Merchant Street', 'Trade Avenue', 'Market Row', 'Commerce Lane', 'Bazaar Way'],
            'craftsmen_quarter': ['Artisan Street', 'Smith Row', 'Craftsman Lane', 'Workshop Way', 'Forge Avenue'],
            'river_ward': ['Dock Street', 'Harbor Way', 'Wharf Lane', 'Sailor Row', 'Quay Avenue'],
        }

        if area_type in street_names:
            street_idx = (row + col) % len(street_names[area_type])
            street = street_names[area_type][street_idx]
            return {
                'name': f'{street}, {area_name}',
                'desc': full_desc,
            }

        return {
            'name': f'{area_name} ({row},{col})',
            'desc': full_desc,
        }


def create_room_grid():
    """Create all rooms in a 32x32 grid."""
    print(f"Creating {GRID_SIZE}x{GRID_SIZE} room grid...")
    print(f"Total rooms to create: {GRID_SIZE * GRID_SIZE}")

    rooms = {}
    created_count = 0

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            area_type = get_area_type(row, col)
            room_data = get_room_data(row, col, area_type)

            # Create room
            room_key = f"vengerberg_{row}_{col}"

            # Check if room already exists
            existing = ObjectDB.objects.filter(db_key=room_key).first()
            if existing:
                print(f"Room {room_key} already exists, skipping...")
                rooms[(row, col)] = existing
                continue

            room = create_object(
                Room,
                key=room_key,
                location=None,
                home=None,  # Don't use default home
            )

            # Set room properties
            room.db.desc = room_data['desc']
            room.db.display_name = room_data['name']
            room.db.area = area_type
            room.db.coordinates = (row, col)

            rooms[(row, col)] = room
            created_count += 1

            if created_count % 100 == 0:
                print(f"Created {created_count} rooms...")

    print(f"Finished creating {created_count} new rooms!")
    return rooms


def connect_rooms(rooms):
    """Create exits connecting all rooms in cardinal directions."""
    print("Connecting rooms with exits...")

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

            if exit_count % 500 == 0:
                print(f"Created {exit_count} exits...")

    print(f"Finished creating {exit_count} exits!")


def set_default_home():
    """Set the default home location to the market square."""
    print("Setting default home location...")

    # Find the market square (18, 16)
    market_square = ObjectDB.objects.filter(db_key="vengerberg_18_16").first()
    if market_square:
        from evennia import settings
        # Note: This would need to be set in settings.py
        print(f"Default home should be set to: {market_square.db.display_name}")
        print(f"Room ID: {market_square.id}")
    else:
        print("Warning: Market square not found!")


def main():
    """Main builder function."""
    print("=" * 60)
    print("VENGERBERG CITY BUILDER")
    print("=" * 60)
    print()

    # Create all rooms
    rooms = create_room_grid()

    print()

    # Connect rooms with exits
    connect_rooms(rooms)

    print()

    # Set default home
    set_default_home()

    print()
    print("=" * 60)
    print("VENGERBERG BUILD COMPLETE!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  Total rooms: {len(rooms)}")
    print(f"  Grid size: {GRID_SIZE}x{GRID_SIZE}")
    print()
    print("Key Locations:")
    print("  Northern Gate: (10, 16)")
    print("  Great Temple: (13, 11)")
    print("  Royal Palace: (13, 21)")
    print("  Central Market: (18, 16)")
    print("  Master Forge: (22, 12)")
    print("  Harbor Master: (22, 22)")
    print("  Iron Mine: (7, 8)")
    print("  Druid Grove: (2, 15)")
    print()


if __name__ == '__main__':
    main()
