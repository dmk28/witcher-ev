# Migration to add crafting system enhancements
# Adds workshop ownership, room purpose, and material quality bonuses

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0013_defaultobject_alter_objectdb_id_defaultcharacter_and_more'),
        ('witcher_rpg', '0005_update_witcher_appearance'),
    ]

    operations = [
        migrations.AddField(
            model_name='witcherroom',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                help_text='Character who owns this room',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='owned_rooms',
                to='objects.objectdb'
            ),
        ),
        migrations.AddField(
            model_name='witcherroom',
            name='room_purpose',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'None'),
                    ('crafting', 'Crafting Workshop'),
                    ('storage', 'Storage/Warehouse'),
                    ('residence', 'Residence'),
                    ('shop', 'Shop/Merchant'),
                    ('tavern', 'Tavern/Inn'),
                ],
                help_text='Purpose of this room (especially for urban areas)',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='itemtemplate',
            name='material_quality_bonus',
            field=models.IntegerField(
                default=0,
                help_text='CR reduction per unit when used as crafting material. Tier I: 0-2, Tier II: 3-7, Tier III: 8-15, Tier IV: 20-35'
            ),
        ),
        migrations.AlterField(
            model_name='itemtemplate',
            name='crafting_difficulty',
            field=models.IntegerField(
                default=10,
                help_text='Base CR to craft this item (affected by material quality)'
            ),
        ),
    ]
