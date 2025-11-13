# Migration to add physical_description field to WitcherCharacter and CharacterGenerationRequest

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('witcher_rpg', '0021_populate_weapons_and_armor'),
    ]

    operations = [
        migrations.AddField(
            model_name='witchercharacter',
            name='physical_description',
            field=models.TextField(blank=True, help_text='Physical appearance: height, build, hair, eyes, distinguishing features, etc.'),
        ),
        migrations.AddField(
            model_name='charactergenerationrequest',
            name='physical_description',
            field=models.TextField(blank=True, help_text='Character physical appearance'),
        ),
    ]
