# Generated manually on 2025-11-11
# Populates sample weapons and armor for all types

from django.db import migrations


def create_weapons_and_armor(apps, schema_editor):
    """Create sample weapons and armor items."""
    ItemTemplate = apps.get_model("witcher_rpg", "ItemTemplate")

    # ========================================
    # WEAPONS - Blades
    # ========================================
    blades_weapons = [
        {
            'name': 'Iron Sword',
            'description': 'A basic iron sword, common among soldiers and guards.',
            'tier': 'tier_1',
            'category': 'weapon',
            'weapon_type': 'blades',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 2,
            'gold_value': 50,
            'weight': 3.0,
        },
        {
            'name': 'Steel Longsword',
            'description': 'A well-crafted steel longsword, balanced and sharp.',
            'tier': 'tier_2',
            'category': 'weapon',
            'weapon_type': 'blades',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 4,
            'gold_value': 150,
            'weight': 3.5,
        },
        {
            'name': 'Silver Sword',
            'description': 'A sword forged with silver, deadly against supernatural creatures.',
            'tier': 'tier_3',
            'category': 'weapon',
            'weapon_type': 'blades',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 6,
            'gold_value': 500,
            'weight': 3.2,
            'special_ability': '+2d damage against monsters and supernatural beings',
        },
        {
            'name': 'Aerondight',
            'description': 'A legendary sword that grows with its wielder, said to be given by the Lady of the Lake.',
            'tier': 'tier_4',
            'category': 'weapon',
            'weapon_type': 'blades',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 8,
            'gold_value': 5000,
            'weight': 3.0,
            'stat_bonuses': {'strength': 2, 'agility': 1},
            'special_ability': 'Gains +1 damage for each successful hit (max +5). Resets on miss.',
        },
        {
            'name': 'Iron Dagger',
            'description': 'A small iron dagger, useful for close quarters.',
            'tier': 'tier_1',
            'category': 'weapon',
            'weapon_type': 'blades',
            'equipment_slot': 'weapon_off',
            'damage_bonus': 1,
            'gold_value': 20,
            'weight': 0.5,
        },
    ]

    # ========================================
    # WEAPONS - Axes
    # ========================================
    axes_weapons = [
        {
            'name': 'Woodcutter Axe',
            'description': 'A simple axe meant for chopping wood, but serviceable in combat.',
            'tier': 'tier_1',
            'category': 'weapon',
            'weapon_type': 'axes',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 3,
            'gold_value': 40,
            'weight': 4.0,
        },
        {
            'name': 'Battle Axe',
            'description': 'A heavy battle axe designed for cleaving through armor and bone.',
            'tier': 'tier_2',
            'category': 'weapon',
            'weapon_type': 'axes',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 5,
            'gold_value': 180,
            'weight': 5.0,
        },
        {
            'name': 'Dwarven Great Axe',
            'description': 'A masterwork axe crafted by dwarven smiths, heavy but devastating.',
            'tier': 'tier_3',
            'category': 'weapon',
            'weapon_type': 'axes',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 7,
            'gold_value': 600,
            'weight': 6.0,
            'stat_bonuses': {'strength': 1},
        },
        {
            'name': 'Mahakam Rune Axe',
            'description': 'An ancient dwarven axe inscribed with powerful runes.',
            'tier': 'tier_4',
            'category': 'weapon',
            'weapon_type': 'axes',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 9,
            'gold_value': 6000,
            'weight': 5.5,
            'stat_bonuses': {'strength': 3, 'endurance': 2},
            'special_ability': 'Ignores 2 points of enemy armor. Critical hits stun for 1 round.',
        },
    ]

    # ========================================
    # WEAPONS - Maces/Hammers
    # ========================================
    maces_weapons = [
        {
            'name': 'Club',
            'description': 'A crude wooden club, better than bare fists.',
            'tier': 'tier_1',
            'category': 'weapon',
            'weapon_type': 'maces',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 2,
            'gold_value': 10,
            'weight': 2.5,
        },
        {
            'name': 'Steel Mace',
            'description': 'A flanged mace designed to crush armor and bones.',
            'tier': 'tier_2',
            'category': 'weapon',
            'weapon_type': 'maces',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 4,
            'gold_value': 120,
            'weight': 3.5,
        },
        {
            'name': 'War Hammer',
            'description': 'A two-handed war hammer capable of shattering plate armor.',
            'tier': 'tier_3',
            'category': 'weapon',
            'weapon_type': 'maces',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 6,
            'gold_value': 450,
            'weight': 6.0,
            'special_ability': 'Ignores 3 points of armor on hit',
        },
        {
            'name': 'Gesheft',
            'description': 'A legendary hammer blessed by the dwarven gods.',
            'tier': 'tier_4',
            'category': 'weapon',
            'weapon_type': 'maces',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 10,
            'gold_value': 7000,
            'weight': 5.0,
            'stat_bonuses': {'strength': 2, 'endurance': 2},
            'special_ability': 'Ignores all armor. Deals double damage to constructs and undead.',
        },
    ]

    # ========================================
    # WEAPONS - Spears/Polearms
    # ========================================
    spears_weapons = [
        {
            'name': 'Spear',
            'description': 'A simple wooden spear with an iron tip.',
            'tier': 'tier_1',
            'category': 'weapon',
            'weapon_type': 'spears',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 3,
            'gold_value': 35,
            'weight': 3.0,
        },
        {
            'name': 'Pike',
            'description': 'A long pike used by infantry to keep enemies at bay.',
            'tier': 'tier_2',
            'category': 'weapon',
            'weapon_type': 'spears',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 4,
            'gold_value': 140,
            'weight': 4.5,
            'special_ability': '+1d damage against charging enemies',
        },
        {
            'name': 'Halberd',
            'description': 'A versatile polearm with an axe blade and spear point.',
            'tier': 'tier_3',
            'category': 'weapon',
            'weapon_type': 'spears',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 6,
            'gold_value': 550,
            'weight': 5.5,
            'stat_bonuses': {'strength': 1},
        },
        {
            'name': 'Gae Bolg',
            'description': 'A cursed spear that never misses its target.',
            'tier': 'tier_4',
            'category': 'weapon',
            'weapon_type': 'spears',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 8,
            'gold_value': 8000,
            'weight': 3.5,
            'stat_bonuses': {'reflexes': 2, 'perception': 1},
            'special_ability': '+2 to hit rolls. On critical hit, target must save or take +3d damage.',
        },
    ]

    # ========================================
    # WEAPONS - Crossbows/Bows
    # ========================================
    ranged_weapons = [
        {
            'name': 'Shortbow',
            'description': 'A simple wooden shortbow for hunting.',
            'tier': 'tier_1',
            'category': 'weapon',
            'weapon_type': 'crossbows',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 2,
            'gold_value': 45,
            'weight': 2.0,
        },
        {
            'name': 'Light Crossbow',
            'description': 'A light crossbow that can be reloaded quickly.',
            'tier': 'tier_2',
            'category': 'weapon',
            'weapon_type': 'crossbows',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 4,
            'gold_value': 160,
            'weight': 4.0,
        },
        {
            'name': 'Heavy Crossbow',
            'description': 'A powerful crossbow capable of piercing heavy armor.',
            'tier': 'tier_3',
            'category': 'weapon',
            'weapon_type': 'crossbows',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 6,
            'gold_value': 520,
            'weight': 6.0,
            'special_ability': 'Ignores 2 points of armor',
        },
        {
            'name': 'Elven Longbow',
            'description': 'An ancient elven bow that fires with supernatural accuracy.',
            'tier': 'tier_4',
            'category': 'weapon',
            'weapon_type': 'crossbows',
            'equipment_slot': 'weapon_main',
            'damage_bonus': 7,
            'gold_value': 5500,
            'weight': 2.5,
            'stat_bonuses': {'agility': 2, 'perception': 2},
            'special_ability': '+3 to hit rolls. Can fire two arrows per round at -2 penalty each.',
        },
    ]

    # ========================================
    # SHIELDS
    # ========================================
    shields = [
        {
            'name': 'Wooden Shield',
            'description': 'A basic wooden shield, better than nothing.',
            'tier': 'tier_1',
            'category': 'shield',
            'equipment_slot': 'shield',
            'armor_value': 2,
            'gold_value': 30,
            'weight': 5.0,
        },
        {
            'name': 'Steel Shield',
            'description': 'A sturdy steel shield that can deflect most blows.',
            'tier': 'tier_2',
            'category': 'shield',
            'equipment_slot': 'shield',
            'armor_value': 4,
            'gold_value': 150,
            'weight': 8.0,
        },
        {
            'name': 'Kite Shield',
            'description': 'A large kite shield offering excellent protection.',
            'tier': 'tier_3',
            'category': 'shield',
            'equipment_slot': 'shield',
            'armor_value': 6,
            'gold_value': 400,
            'weight': 10.0,
            'stat_bonuses': {'endurance': 1},
        },
        {
            'name': 'Aegis of Kings',
            'description': 'A legendary shield said to have protected ancient kings.',
            'tier': 'tier_4',
            'category': 'shield',
            'equipment_slot': 'shield',
            'armor_value': 8,
            'gold_value': 6000,
            'weight': 7.0,
            'stat_bonuses': {'endurance': 2, 'willpower': 1},
            'special_ability': 'Once per day, can negate one attack completely.',
        },
    ]

    # ========================================
    # ARMOR - Light
    # ========================================
    light_armor = [
        {
            'name': 'Leather Jerkin',
            'description': 'Basic leather armor offering minimal protection.',
            'tier': 'tier_1',
            'category': 'armor',
            'armor_type': 'light',
            'equipment_slot': 'chest',
            'armor_value': 2,
            'gold_value': 50,
            'weight': 8.0,
        },
        {
            'name': 'Studded Leather Armor',
            'description': 'Leather armor reinforced with metal studs.',
            'tier': 'tier_2',
            'category': 'armor',
            'armor_type': 'light',
            'equipment_slot': 'chest',
            'armor_value': 4,
            'gold_value': 180,
            'weight': 10.0,
            'stat_bonuses': {'agility': 1},
        },
        {
            'name': 'Elven Leather Armor',
            'description': 'Supple elven leather that doesn\'t restrict movement.',
            'tier': 'tier_3',
            'category': 'armor',
            'armor_type': 'light',
            'equipment_slot': 'chest',
            'armor_value': 6,
            'gold_value': 550,
            'weight': 7.0,
            'stat_bonuses': {'agility': 2, 'reflexes': 1},
        },
        {
            'name': 'Leather Boots',
            'description': 'Comfortable leather boots.',
            'tier': 'tier_1',
            'category': 'armor',
            'armor_type': 'light',
            'equipment_slot': 'feet',
            'armor_value': 1,
            'gold_value': 20,
            'weight': 2.0,
        },
        {
            'name': 'Leather Gloves',
            'description': 'Basic leather gloves.',
            'tier': 'tier_1',
            'category': 'armor',
            'armor_type': 'light',
            'equipment_slot': 'hands',
            'armor_value': 1,
            'gold_value': 15,
            'weight': 1.0,
        },
    ]

    # ========================================
    # ARMOR - Medium
    # ========================================
    medium_armor = [
        {
            'name': 'Chainmail Shirt',
            'description': 'A shirt of interlocking steel rings.',
            'tier': 'tier_2',
            'category': 'armor',
            'armor_type': 'medium',
            'equipment_slot': 'chest',
            'armor_value': 6,
            'gold_value': 300,
            'weight': 20.0,
        },
        {
            'name': 'Scale Mail',
            'description': 'Armor made from overlapping metal scales.',
            'tier': 'tier_3',
            'category': 'armor',
            'armor_type': 'medium',
            'equipment_slot': 'chest',
            'armor_value': 8,
            'gold_value': 700,
            'weight': 25.0,
            'stat_bonuses': {'endurance': 1},
        },
        {
            'name': 'Chainmail Leggings',
            'description': 'Chain leggings for leg protection.',
            'tier': 'tier_2',
            'category': 'armor',
            'armor_type': 'medium',
            'equipment_slot': 'legs',
            'armor_value': 3,
            'gold_value': 150,
            'weight': 12.0,
        },
        {
            'name': 'Steel Gauntlets',
            'description': 'Heavy steel gauntlets.',
            'tier': 'tier_2',
            'category': 'armor',
            'armor_type': 'medium',
            'equipment_slot': 'hands',
            'armor_value': 2,
            'gold_value': 80,
            'weight': 4.0,
        },
    ]

    # ========================================
    # ARMOR - Heavy
    # ========================================
    heavy_armor = [
        {
            'name': 'Plate Cuirass',
            'description': 'A heavy plate chest piece offering excellent protection.',
            'tier': 'tier_3',
            'category': 'armor',
            'armor_type': 'heavy',
            'equipment_slot': 'chest',
            'armor_value': 10,
            'gold_value': 1000,
            'weight': 35.0,
            'stat_bonuses': {'endurance': 2},
        },
        {
            'name': 'Full Plate Armor',
            'description': 'Complete plate armor covering the entire body.',
            'tier': 'tier_4',
            'category': 'armor',
            'armor_type': 'heavy',
            'equipment_slot': 'chest',
            'armor_value': 15,
            'gold_value': 8000,
            'weight': 50.0,
            'stat_bonuses': {'endurance': 3, 'strength': 1},
            'special_ability': 'Resistance to piercing damage. -1 to agility-based rolls.',
        },
        {
            'name': 'Plate Helm',
            'description': 'A sturdy plate helmet.',
            'tier': 'tier_3',
            'category': 'armor',
            'armor_type': 'heavy',
            'equipment_slot': 'head',
            'armor_value': 3,
            'gold_value': 200,
            'weight': 5.0,
        },
        {
            'name': 'Plate Greaves',
            'description': 'Heavy plate leg armor.',
            'tier': 'tier_3',
            'category': 'armor',
            'armor_type': 'heavy',
            'equipment_slot': 'legs',
            'armor_value': 4,
            'gold_value': 350,
            'weight': 15.0,
        },
        {
            'name': 'Plate Gauntlets',
            'description': 'Articulated plate gauntlets.',
            'tier': 'tier_3',
            'category': 'armor',
            'armor_type': 'heavy',
            'equipment_slot': 'hands',
            'armor_value': 2,
            'gold_value': 150,
            'weight': 6.0,
        },
        {
            'name': 'Plate Sabatons',
            'description': 'Heavy plate boots.',
            'tier': 'tier_3',
            'category': 'armor',
            'armor_type': 'heavy',
            'equipment_slot': 'feet',
            'armor_value': 2,
            'gold_value': 120,
            'weight': 8.0,
        },
    ]

    # Create all items
    all_items = (
        blades_weapons + axes_weapons + maces_weapons +
        spears_weapons + ranged_weapons + shields +
        light_armor + medium_armor + heavy_armor
    )

    for item_data in all_items:
        ItemTemplate.objects.create(**item_data)


def delete_weapons_and_armor(apps, schema_editor):
    """Remove sample weapons and armor."""
    ItemTemplate = apps.get_model("witcher_rpg", "ItemTemplate")

    # Delete all weapons, shields, and armor
    ItemTemplate.objects.filter(category__in=['weapon', 'shield', 'armor']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("witcher_rpg", "0020_weapon_armor_equipment_system"),
    ]

    operations = [
        migrations.RunPython(create_weapons_and_armor, delete_weapons_and_armor),
    ]
