# Migration to add Artisan vocation and populate vocation skill cost multipliers
# Artisans pay less for crafting skills, warriors pay less for combat skills, etc.

from django.db import migrations


def add_artisan_vocation(apps, schema_editor):
    """Add the Artisan vocation with appropriate stats and skills."""
    Vocation = apps.get_model('witcher_rpg', 'Vocation')
    VocationFeat = apps.get_model('witcher_rpg', 'VocationFeat')

    # Create Artisan vocation
    artisan, created = Vocation.objects.get_or_create(
        name='artisan',  # Use lowercase to match VOCATION_CHOICES format
        defaults={
            'description': (
                'Master craftspeople who create the finest weapons, armor, potions, and '
                'magical items. Artisans are found in cities and villages across the world, '
                'running forges, workshops, and laboratories. They possess exceptional technical '
                'skill and knowledge of materials.'
            ),
            # Stat modifiers
            'intelligence_mod': 2,  # Technical knowledge
            'perception_mod': 2,    # Attention to detail
            'willpower_mod': 1,     # Patience and focus
            'wit_mod': 1,           # Problem-solving
            # Skill access
            'has_crafting': True,
            'has_alchemy': True,
            # Default skills
            'default_skills': {
                'crafting_skill': 4,      # Core competency
                'alchemy': 3,             # Potion-making
                'resist_coercion': 2,     # Professional pride
                'perception': 3,          # Quality assessment
                'business': 3,            # Running a workshop
                'education': 2,           # Technical knowledge
                'material_knowledge': 3,  # Understanding materials
            }
        }
    )

    if created:
        # Add Artisan-specific feats
        VocationFeat.objects.create(
            vocation=artisan,
            name='Master Craftsman',
            description='Reduce crafting difficulty by 10 for all recipes. Gain +2 to all crafting skill checks.'
        )

        VocationFeat.objects.create(
            vocation=artisan,
            name='Material Expertise',
            description='Can identify material quality at a glance. Knows where to source rare materials.'
        )

        VocationFeat.objects.create(
            vocation=artisan,
            name='Workshop Efficiency',
            description='Crafting time reduced by 25%. Can work on multiple projects simultaneously.'
        )

        VocationFeat.objects.create(
            vocation=artisan,
            name='Quality Control',
            description='Failed crafting attempts only consume 50% of materials instead of 100%.'
        )


def populate_vocation_multipliers(apps, schema_editor):
    """
    Populate default vocation skill cost multipliers.

    Philosophy:
    - Specialists pay 0.5x-0.75x (half to 3/4 cost)
    - Normal vocations pay 1.0x (unchanged)
    - Non-specialists pay 1.5x-2.0x (1.5x to 2x cost)
    """
    Vocation = apps.get_model('witcher_rpg', 'Vocation')
    VocationSkillCostMultiplier = apps.get_model('witcher_rpg', 'VocationSkillCostMultiplier')

    # Get all vocations
    try:
        witcher = Vocation.objects.get(name='Witcher')
        soldier = Vocation.objects.get(name='Soldier')
        merchant = Vocation.objects.get(name='Merchant')
        artisan = Vocation.objects.get(name='Artisan')
    except Vocation.DoesNotExist:
        # If vocations don't exist yet, skip this migration
        return

    # Define multipliers for each vocation
    # Format: (vocation, skill_name, multiplier)
    multipliers = [
        # ARTISAN - Crafting specialist
        (artisan, 'crafting_skill', 0.5),      # Core skill, half cost
        (artisan, 'alchemy', 0.5),             # Core skill, half cost
        (artisan, 'material_knowledge', 0.5),  # Core skill, half cost
        (artisan, 'runecrafting', 0.75),       # Related skill, 3/4 cost
        (artisan, 'jewelcrafting', 0.75),      # Related skill, 3/4 cost
        (artisan, 'weaponsmithing', 0.75),     # Related skill, 3/4 cost
        (artisan, 'armorsmithing', 0.75),      # Related skill, 3/4 cost
        (artisan, 'tailoring', 0.75),          # Related skill, 3/4 cost
        (artisan, 'blades', 1.5),              # Non-combat vocation
        (artisan, 'brawling', 1.5),            # Non-combat vocation
        (artisan, 'crossbows', 1.5),           # Non-combat vocation

        # MERCHANT - Business and social specialist
        (merchant, 'business', 0.5),           # Core skill, half cost
        (merchant, 'persuasion', 0.5),         # Core skill, half cost
        (merchant, 'deduction', 0.5),          # Core skill, half cost
        (merchant, 'charm', 0.75),             # Related social skill
        (merchant, 'cunning', 0.75),           # Related social skill
        (merchant, 'haggling', 0.5),           # Core skill, half cost
        (merchant, 'crafting_skill', 0.75),    # Can craft goods to sell
        (merchant, 'alchemy', 0.75),           # Can make potions to sell
        (merchant, 'blades', 1.5),             # Non-combat vocation
        (merchant, 'brawling', 1.5),           # Non-combat vocation

        # WITCHER - Combat and monster hunting specialist
        (witcher, 'blades', 0.5),              # Core skill, half cost
        (witcher, 'brawling', 0.5),            # Core skill, half cost
        (witcher, 'athletics', 0.5),           # Core skill, half cost
        (witcher, 'sign_sorcery', 0.5),        # Core skill, half cost
        (witcher, 'monster_lore', 0.5),        # Core skill, half cost
        (witcher, 'tracking', 0.5),            # Core skill, half cost
        (witcher, 'alchemy', 0.75),            # Witchers brew potions
        (witcher, 'crafting_skill', 1.5),      # Not a craftsman
        (witcher, 'business', 2.0),            # Very non-commercial
        (witcher, 'charm', 1.5),               # Not socially adept

        # SOLDIER - Military combat specialist
        (soldier, 'blades', 0.5),              # Core skill, half cost
        (soldier, 'brawling', 0.5),            # Core skill, half cost
        (soldier, 'crossbows', 0.5),           # Core skill, half cost
        (soldier, 'athletics', 0.5),           # Core skill, half cost
        (soldier, 'riding', 0.75),             # Military skill
        (soldier, 'tactics', 0.5),             # Military skill, half cost
        (soldier, 'leadership', 0.75),         # Military skill
        (soldier, 'alchemy', 1.5),             # Not an alchemist
        (soldier, 'crafting_skill', 1.5),      # Not a craftsman
        (soldier, 'business', 2.0),            # Very non-commercial
        (soldier, 'charm', 1.5),               # Not socially focused
    ]

    # Create multipliers
    for vocation, skill_name, multiplier in multipliers:
        VocationSkillCostMultiplier.objects.get_or_create(
            vocation=vocation,
            skill_name=skill_name,
            defaults={'multiplier': multiplier}
        )


def remove_artisan_vocation(apps, schema_editor):
    """Remove Artisan vocation if migration is reversed."""
    Vocation = apps.get_model('witcher_rpg', 'Vocation')
    try:
        artisan = Vocation.objects.get(name='artisan')
        artisan.delete()
    except Vocation.DoesNotExist:
        pass


def remove_vocation_multipliers(apps, schema_editor):
    """Remove all vocation multipliers if migration is reversed."""
    VocationSkillCostMultiplier = apps.get_model('witcher_rpg', 'VocationSkillCostMultiplier')
    VocationSkillCostMultiplier.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('witcher_rpg', '0014_itemset_craftingrecipe_craftingattempt_and_more'),
    ]

    operations = [
        migrations.RunPython(add_artisan_vocation, remove_artisan_vocation),
        migrations.RunPython(populate_vocation_multipliers, remove_vocation_multipliers),
    ]
