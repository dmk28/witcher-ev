# Generated manually on 2025-11-11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("witcher_rpg", "0019_organization_income_system"),
    ]

    operations = [
        migrations.AddField(
            model_name="itemtemplate",
            name="weapon_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("blades", "Blades (Swords, Daggers)"),
                    ("axes", "Axes (Axes, Hatchets)"),
                    ("maces", "Maces (Maces, Hammers, Clubs)"),
                    ("spears", "Spears (Spears, Polearms, Halberds)"),
                    ("crossbows", "Crossbows (Crossbows, Bows)"),
                    ("brawling", "Brawling (Fists, Gauntlets)"),
                ],
                help_text="Type of weapon (links to skill)",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="itemtemplate",
            name="armor_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("light", "Light Armor (Leather, Cloth)"),
                    ("medium", "Medium Armor (Studded, Chain)"),
                    ("heavy", "Heavy Armor (Plate, Full Plate)"),
                ],
                help_text="Type of armor (light/medium/heavy)",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="itemtemplate",
            name="equipment_slot",
            field=models.CharField(
                blank=True,
                choices=[
                    ("weapon_main", "Main Hand Weapon"),
                    ("weapon_off", "Off-Hand Weapon"),
                    ("shield", "Shield"),
                    ("head", "Head/Helmet"),
                    ("chest", "Chest/Torso"),
                    ("legs", "Legs/Greaves"),
                    ("feet", "Feet/Boots"),
                    ("hands", "Hands/Gauntlets"),
                    ("back", "Back/Cloak"),
                    ("neck", "Neck/Amulet"),
                    ("ring_1", "Ring Slot 1"),
                    ("ring_2", "Ring Slot 2"),
                ],
                help_text="Equipment slot this item occupies",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="itemtemplate",
            name="category",
            field=models.CharField(
                choices=[
                    ("weapon", "Weapon"),
                    ("armor", "Armor"),
                    ("shield", "Shield"),
                    ("consumable", "Consumable"),
                    ("material", "Crafting Material"),
                    ("quest", "Quest Item"),
                    ("misc", "Miscellaneous"),
                ],
                default="misc",
                help_text="Item category",
                max_length=20,
            ),
        ),
    ]
