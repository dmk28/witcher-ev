# Migration to add vocation skill packages and support skills
# Adds resistance, leadership, tactics skills and default_skills for vocations

from django.db import migrations, models


def populate_skill_packages(apps, schema_editor):
    """
    Populate default skill packages for all vocations.
    """
    Vocation = apps.get_model('witcher_rpg', 'Vocation')

    skill_packages = {
        # Soldier: Athletics, spears (polearms), secondary weapon, leadership, tactics, resistance
        'soldier': {
            'athletics': 2,
            'spears': 3,          # Primary weapon (polearms)
            'axes': 2,            # Secondary weapon
            'resistance': 2,      # Soak skill
            'leadership': 2,      # Military leadership
            'tactics': 2,         # Battlefield strategy
        },

        # Bladesman: Master swordsmen
        'bladesman': {
            'blades': 4,          # Primary weapon (master level)
            'athletics': 2,
            'resistance': 1,
        },

        # Knight: Armored warriors
        'knight': {
            'blades': 2,          # Swords
            'maces': 2,           # Secondary (for armored foes)
            'athletics': 2,
            'resistance': 3,      # Heavy armor training
            'leadership': 1,
        },

        # Witcher: Sign sorcery, athletics, resistance, swords, crossbows, alchemy
        'witcher': {
            'sign_sorcery': 2,    # Witcher signs
            'blades': 3,          # Silver and steel swords
            'crossbows': 2,       # Ranged combat
            'alchemy': 2,         # Potions and oils
            'athletics': 2,
            'resistance': 2,      # Mutations provide resilience
        },

        # Sorcerer: Magic focus
        'sorcerer': {
            'magery': 3,          # Primary skill
            'alchemy': 1,
            'athletics': 1,
        },

        # Inquisitor: Hunter of heretics
        'inquisitor': {
            'crossbows': 2,       # Ranged expertise
            'maces': 2,           # Melee
            'athletics': 2,
            'tactics': 2,         # Hunt planning
            'resistance': 1,
        },

        # Courtesan: Social expert
        'courtesan': {
            'athletics': 1,
            # Social skills would go here (charm, persuasion, etc.)
            # But those are stats, not skills
        },

        # Infiltrator: Stealth and subterfuge
        'infiltrator': {
            'blades': 2,          # Daggers, light weapons
            'crossbows': 1,       # Silent kills
            'alchemy': 1,         # Poisons
            'athletics': 3,       # Climbing, sneaking
            'resistance': 1,
        },

        # Noble: Leadership and command
        'noble': {
            'blades': 1,          # Dueling
            'leadership': 3,      # Primary skill
            'tactics': 2,         # Strategic mind
            'athletics': 1,
        },

        # Alchemist: Potion master
        'alchemist': {
            'alchemy': 4,         # Master level
            'crossbows': 1,       # Some combat training
            'athletics': 1,
        },

        # Merchant: Trade and negotiation
        'merchant': {
            'blades': 1,          # Self-defense
            'athletics': 1,
            'leadership': 1,      # Managing caravans
        },
    }

    for vocation_name, skills in skill_packages.items():
        try:
            vocation = Vocation.objects.get(name=vocation_name)
            vocation.default_skills = skills
            vocation.save()
            print(f"Updated skill package for {vocation_name}: {skills}")
        except Vocation.DoesNotExist:
            print(f"Warning: Vocation '{vocation_name}' not found")


def reverse_populate_skill_packages(apps, schema_editor):
    """
    Clear all skill packages.
    """
    Vocation = apps.get_model('witcher_rpg', 'Vocation')
    Vocation.objects.all().update(default_skills={})


class Migration(migrations.Migration):

    dependencies = [
        ('witcher_rpg', '0006_crafting_system_enhancements'),
    ]

    operations = [
        # Add new skills to CharacterSkills
        migrations.AddField(
            model_name='characterskills',
            name='resistance',
            field=models.IntegerField(
                default=0,
                help_text='Physical resistance, damage reduction (used for soak)',
                validators=[
                    models.validators.MinValueValidator(0),
                    models.validators.MaxValueValidator(10)
                ]
            ),
        ),
        migrations.AddField(
            model_name='characterskills',
            name='leadership',
            field=models.IntegerField(
                default=0,
                help_text='Military leadership, commanding troops, inspiring allies',
                validators=[
                    models.validators.MinValueValidator(0),
                    models.validators.MaxValueValidator(10)
                ]
            ),
        ),
        migrations.AddField(
            model_name='characterskills',
            name='tactics',
            field=models.IntegerField(
                default=0,
                help_text='Tactical planning, battlefield strategy, military knowledge',
                validators=[
                    models.validators.MinValueValidator(0),
                    models.validators.MaxValueValidator(10)
                ]
            ),
        ),
        # Add default_skills to Vocation
        migrations.AddField(
            model_name='vocation',
            name='default_skills',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Starting skill levels for this vocation: {'blades': 3, 'athletics': 2, ...}"
            ),
        ),
        # Populate skill packages
        migrations.RunPython(populate_skill_packages, reverse_populate_skill_packages),
    ]
