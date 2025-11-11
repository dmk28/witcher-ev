# Migration to add social rank system
# Adds social_rank field to WitcherCharacter with vocation-based restrictions

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('witcher_rpg', '0008_character_creation_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='witchercharacter',
            name='social_rank',
            field=models.IntegerField(
                choices=[
                    (1, 'Rank 1 - Outcast (+5 CR: tests harder)'),
                    (2, 'Rank 2 - Commoner (+0 CR: normal)'),
                    (3, 'Rank 3 - Knight/Small Gentry (-5 CR: tests easier)'),
                    (4, 'Rank 4 - Landed Gentry (-10 CR: tests easier)'),
                    (5, 'Rank 5 - Royalty (-20 CR: tests much easier)'),
                ],
                default=2,
                help_text='Social standing (affects CR for most rolls). Witchers: 1-2, Sorcerers: 3-4, Others: 1-5',
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5)
                ]
            ),
        ),
    ]
