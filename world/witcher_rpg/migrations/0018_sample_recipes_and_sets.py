# Migration to populate sample crafting recipes and item sets
# Demonstrates the advanced crafting system with Witcher-themed content

from django.db import migrations


def create_sample_item_sets(apps, schema_editor):
    """Create sample item sets (Witcher Schools gear)."""
    ItemSet = apps.get_model('witcher_rpg', 'ItemSet')

    # Cat School Witcher Gear - Fast attack focused
    ItemSet.objects.get_or_create(
        name='Cat School Gear',
        defaults={
            'description': (
                'Lightweight armor crafted by the Cat School of witchers. '
                'Emphasizes speed, agility, and precision strikes. The gear is '
                'particularly effective for assassins and duelists who rely on '
                'quick movements and deadly accuracy.'
            ),
            'set_type': 'mixed',
            'tier': 3,
            'two_piece_bonus': {
                'stat': 'agility',
                'value': 1,
                'description': '+1 Agility'
            },
            'three_piece_bonus': {
                'stat': 'reflexes',
                'value': 1,
                'attack_speed_bonus': 10,
                'description': '+1 Reflexes, +10% Attack Speed'
            },
            'four_piece_bonus': {
                'critical_damage': 25,
                'description': '+25% Critical Hit Damage'
            },
            'five_piece_bonus': {
                'stat': 'perception',
                'value': 1,
                'backstab_bonus': 50,
                'description': '+1 Perception, +50% Backstab Damage'
            }
        }
    )

    # Wolf School Witcher Gear - Balanced approach
    ItemSet.objects.get_or_create(
        name='Wolf School Gear',
        defaults={
            'description': (
                'Balanced armor representing the Wolf School tradition. '
                'Provides good protection without sacrificing mobility. '
                'This is the signature gear of Kaer Morhen witchers, '
                'emphasizing versatility and adaptability in combat.'
            ),
            'set_type': 'mixed',
            'tier': 3,
            'two_piece_bonus': {
                'stat': 'endurance',
                'value': 1,
                'description': '+1 Endurance'
            },
            'three_piece_bonus': {
                'sign_intensity': 15,
                'damage_bonus': 10,
                'description': '+15% Sign Intensity, +10% Attack Damage'
            },
            'four_piece_bonus': {
                'stat': 'strength',
                'value': 1,
                'armor_bonus': 10,
                'description': '+1 Strength, +10 Armor'
            },
            'five_piece_bonus': {
                'adrenaline_gain': 25,
                'stamina_regen': 20,
                'description': '+25% Adrenaline Gain, +20% Stamina Regen'
            }
        }
    )

    # Bear School Witcher Gear - Heavy armor tank
    ItemSet.objects.get_or_create(
        name='Bear School Gear',
        defaults={
            'description': (
                'Heavy armor forged by the Bear School. Provides exceptional '
                'protection at the cost of mobility. Bear School witchers favor '
                'overwhelming force and resilience, standing their ground against '
                'the fiercest monsters.'
            ),
            'set_type': 'armor',
            'tier': 4,
            'two_piece_bonus': {
                'armor_bonus': 20,
                'description': '+20 Armor'
            },
            'three_piece_bonus': {
                'stat': 'endurance',
                'value': 2,
                'damage_reduction': 10,
                'description': '+2 Endurance, +10% Damage Reduction'
            },
            'four_piece_bonus': {
                'stat': 'strength',
                'value': 1,
                'melee_damage': 20,
                'description': '+1 Strength, +20% Melee Damage'
            },
            'five_piece_bonus': {
                'stat': 'willpower',
                'value': 1,
                'resistance_all': 15,
                'description': '+1 Willpower, +15% All Resistances'
            }
        }
    )

    # Griffin School Witcher Gear - Sign magic focused
    ItemSet.objects.get_or_create(
        name='Griffin School Gear',
        defaults={
            'description': (
                'Armor designed by the scholarly Griffin School. Enhances '
                'magical abilities and sign casting. Griffin witchers are '
                'known for their mastery of signs and alchemical preparations, '
                'preferring tactical advantages over brute force.'
            ),
            'set_type': 'mixed',
            'tier': 4,
            'two_piece_bonus': {
                'sign_intensity': 25,
                'description': '+25% Sign Intensity'
            },
            'three_piece_bonus': {
                'stat': 'intelligence',
                'value': 1,
                'stamina_cost_reduction': 15,
                'description': '+1 Intelligence, -15% Sign Stamina Cost'
            },
            'four_piece_bonus': {
                'stat': 'willpower',
                'value': 2,
                'sign_duration': 25,
                'description': '+2 Willpower, +25% Sign Duration'
            },
            'five_piece_bonus': {
                'spell_damage': 50,
                'mana_regen': 30,
                'description': '+50% Spell Damage, +30% Mana Regen'
            }
        }
    )


def create_sample_recipes(apps, schema_editor):
    """Create sample crafting recipes for tier III-IV items."""
    CraftingRecipe = apps.get_model('witcher_rpg', 'CraftingRecipe')
    ItemTemplate = apps.get_model('witcher_rpg', 'ItemTemplate')
    ItemSet = apps.get_model('witcher_rpg', 'ItemSet')

    # Get item sets
    try:
        cat_set = ItemSet.objects.get(name='Cat School Gear')
        wolf_set = ItemSet.objects.get(name='Wolf School Gear')
        bear_set = ItemSet.objects.get(name='Bear School Gear')
        griffin_set = ItemSet.objects.get(name='Griffin School Gear')
    except ItemSet.DoesNotExist:
        # Sets not created yet, skip
        return

    # We'll reference item templates by creating them or getting existing ones
    # For this example, we'll just create the recipes without linking to actual items
    # In production, you'd create the ItemTemplate objects first

    # ===== WEAPONSMITHING RECIPES =====

    CraftingRecipe.objects.get_or_create(
        name='Moonblade Silver Sword Formula',
        defaults={
            'result_item': None,  # Would link to ItemTemplate in production
            'crafting_type': 'weaponsmithing',
            'min_skill_level': 6,
            'base_difficulty': 60,
            'required_materials': {
                'silver_ingot': 8,
                'moonstone': 3,
                'monster_essence': 5,
                'dimeritium_ore': 2,
                'leather_straps': 4
            },
            'required_workshop': 'forge',
            'time_required_minutes': 180,
            'xp_reward': 100,
            'gold_cost': 500,
            'is_rare': True,
            'discovery_location': (
                'Found in the ruins of an ancient elven smithy near Loc Muinne. '
                'The formula requires precise lunar timing - must be crafted during a full moon.'
            ),
            'set_piece': None
        }
    )

    CraftingRecipe.objects.get_or_create(
        name='Cat School Silver Sword',
        defaults={
            'result_item': None,
            'crafting_type': 'weaponsmithing',
            'min_skill_level': 5,
            'base_difficulty': 55,
            'required_materials': {
                'silver_ingot': 6,
                'steel_ingot': 3,
                'cat_school_diagram': 1,
                'leather_straps': 3,
                'ruby': 1
            },
            'required_workshop': 'forge',
            'time_required_minutes': 120,
            'xp_reward': 75,
            'gold_cost': 300,
            'is_rare': True,
            'discovery_location': 'Cat School diagrams can be found in Velen, hidden in bandit camps.',
            'set_piece': cat_set
        }
    )

    # ===== ARMORSMITHING RECIPES =====

    CraftingRecipe.objects.get_or_create(
        name='Bear School Armor',
        defaults={
            'result_item': None,
            'crafting_type': 'armorsmithing',
            'min_skill_level': 7,
            'base_difficulty': 70,
            'required_materials': {
                'steel_plate': 12,
                'hardened_leather': 8,
                'bear_school_diagram': 1,
                'dimeritium_plate': 4,
                'bear_hide': 6
            },
            'required_workshop': 'forge',
            'time_required_minutes': 240,
            'xp_reward': 150,
            'gold_cost': 800,
            'is_rare': True,
            'discovery_location': 'Bear School diagrams are scattered across Skellige islands.',
            'set_piece': bear_set
        }
    )

    CraftingRecipe.objects.get_or_create(
        name='Griffin School Armor',
        defaults={
            'result_item': None,
            'crafting_type': 'armorsmithing',
            'min_skill_level': 6,
            'base_difficulty': 65,
            'required_materials': {
                'steel_plate': 8,
                'hardened_leather': 6,
                'griffin_school_diagram': 1,
                'dimeritium_plate': 3,
                'griffin_feather': 4,
                'monster_essence': 3
            },
            'required_workshop': 'forge',
            'time_required_minutes': 200,
            'xp_reward': 125,
            'gold_cost': 600,
            'is_rare': True,
            'discovery_location': 'Griffin School diagrams found in Velen and Novigrad.',
            'set_piece': griffin_set
        }
    )

    # ===== ALCHEMY RECIPES =====

    CraftingRecipe.objects.get_or_create(
        name='Superior Swallow Potion',
        defaults={
            'result_item': None,
            'crafting_type': 'alchemy',
            'min_skill_level': 5,
            'base_difficulty': 50,
            'required_materials': {
                'celandine': 5,
                'drowner_brain': 3,
                'vitriol': 2,
                'rebis': 1
            },
            'required_workshop': 'laboratory',
            'time_required_minutes': 60,
            'xp_reward': 60,
            'gold_cost': 100,
            'is_rare': False,
            'discovery_location': 'Learned from master alchemists in Oxenfurt Academy.',
            'set_piece': None
        }
    )

    CraftingRecipe.objects.get_or_create(
        name='Black Blood Potion (Enhanced)',
        defaults={
            'result_item': None,
            'crafting_type': 'alchemy',
            'min_skill_level': 6,
            'base_difficulty': 55,
            'required_materials': {
                'black_blood_base': 1,
                'vampire_blood': 3,
                'sewant_mushrooms': 4,
                'vitriol': 3,
                'aether': 2
            },
            'required_workshop': 'laboratory',
            'time_required_minutes': 90,
            'xp_reward': 80,
            'gold_cost': 200,
            'is_rare': True,
            'discovery_location': 'Formula discovered in vampire lairs, particularly effective against nekkers.',
            'set_piece': None
        }
    )

    # ===== RUNECRAFTING RECIPES =====

    CraftingRecipe.objects.get_or_create(
        name='Greater Igni Runestone',
        defaults={
            'result_item': None,
            'crafting_type': 'runecrafting',
            'min_skill_level': 7,
            'base_difficulty': 75,
            'required_materials': {
                'ruby': 3,
                'fire_elemental_essence': 5,
                'dimeritium_dust': 4,
                'infused_shard': 6
            },
            'required_workshop': 'enchanting_table',
            'time_required_minutes': 150,
            'xp_reward': 120,
            'gold_cost': 500,
            'is_rare': True,
            'discovery_location': (
                'Ancient rune formula from the elven ruins. Requires understanding of '
                'elemental magic and precise gem cutting.'
            ),
            'set_piece': None
        }
    )

    CraftingRecipe.objects.get_or_create(
        name='Armor Enhancement Rune',
        defaults={
            'result_item': None,
            'crafting_type': 'runecrafting',
            'min_skill_level': 6,
            'base_difficulty': 60,
            'required_materials': {
                'diamond': 2,
                'monster_essence': 4,
                'dimeritium_dust': 3,
                'infused_shard': 4
            },
            'required_workshop': 'enchanting_table',
            'time_required_minutes': 120,
            'xp_reward': 100,
            'gold_cost': 400,
            'is_rare': True,
            'discovery_location': 'Taught by master enchanters in larger cities.',
            'set_piece': None
        }
    )


def remove_sample_data(apps, schema_editor):
    """Remove sample data if migration is reversed."""
    ItemSet = apps.get_model('witcher_rpg', 'ItemSet')
    CraftingRecipe = apps.get_model('witcher_rpg', 'CraftingRecipe')

    # Remove sets
    ItemSet.objects.filter(
        name__in=[
            'Cat School Gear',
            'Wolf School Gear',
            'Bear School Gear',
            'Griffin School Gear'
        ]
    ).delete()

    # Remove recipes
    CraftingRecipe.objects.filter(
        name__in=[
            'Moonblade Silver Sword Formula',
            'Cat School Silver Sword',
            'Bear School Armor',
            'Griffin School Armor',
            'Superior Swallow Potion',
            'Black Blood Potion (Enhanced)',
            'Greater Igni Runestone',
            'Armor Enhancement Rune'
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('witcher_rpg', '0017_alter_craftingrecipe_result_item_alter_vocation_name'),
    ]

    operations = [
        migrations.RunPython(create_sample_item_sets, remove_sample_data),
        migrations.RunPython(create_sample_recipes, remove_sample_data),
    ]
