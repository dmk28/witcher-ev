# Migration to add character creation point-buy system and countries
# Adds Country model, replaces nation CharField with country ForeignKey
# Populates countries with non-physical stat bonuses

from django.db import migrations, models
import django.db.models.deletion


def populate_countries(apps, schema_editor):
    """
    Populate countries with their cultural stat bonuses (non-physical only).
    """
    Country = apps.get_model('witcher_rpg', 'Country')

    countries_data = [
        {
            'name': 'nilfgaard',
            'description': 'The Nilfgaardian Empire: A vast, sophisticated empire known for its scholars, bureaucracy, and cultural refinement.',
            'bonus_stat': 'intelligence',  # Scholarly empire
        },
        {
            'name': 'temeria',
            'description': 'Kingdom of Temeria: A free kingdom known for its resilient people and strong will to resist oppression.',
            'bonus_stat': 'willpower',  # Free kingdom spirit
        },
        {
            'name': 'redania',
            'description': 'Kingdom of Redania: Home to powerful spy networks and political intrigue, master manipulators.',
            'bonus_stat': 'cunning',  # Espionage and manipulation
        },
        {
            'name': 'skellige',
            'description': 'Skellige Isles: Independent warrior clans with iron wills, resistant to outside influence.',
            'bonus_stat': 'willpower',  # Independent, strong-willed
        },
        {
            'name': 'kovir',
            'description': 'Kovir and Poviss: Wealthy northern kingdoms known for education, banking, and scholarship.',
            'bonus_stat': 'intelligence',  # Educated, wealthy
        },
        {
            'name': 'cintra',
            'description': 'Kingdom of Cintra: Known for diplomatic prowess and charm, the Lion Cub of Cintra.',
            'bonus_stat': 'charm',  # Diplomatic nation
        },
        {
            'name': 'aedirn',
            'description': 'Kingdom of Aedirn: A vigilant border kingdom, always watching for threats.',
            'bonus_stat': 'perception',  # Vigilant, watchful
        },
        {
            'name': 'kaedwen',
            'description': 'Kingdom of Kaedwen: Hardy northerners known for quick thinking and adaptability.',
            'bonus_stat': 'wit',  # Hardy, quick-witted
        },
        {
            'name': 'lyria',
            'description': 'Lyria and Rivia: Known for grace and refinement despite being smaller kingdoms.',
            'bonus_stat': 'graces',  # Graceful and refined
        },
        {
            'name': 'cidaris',
            'description': 'Cidaris: Coastal kingdom known for beauty and aesthetics.',
            'bonus_stat': 'appearance',  # Focus on beauty
        },
    ]

    for country_data in countries_data:
        Country.objects.create(**country_data)
        print(f"Created country: {country_data['name']} (+1 {country_data['bonus_stat']})")


def reverse_populate_countries(apps, schema_editor):
    """Clear all countries."""
    Country = apps.get_model('witcher_rpg', 'Country')
    Country.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0013_defaultobject_alter_objectdb_id_defaultcharacter_and_more'),
        ('witcher_rpg', '0007_vocation_skill_packages'),
    ]

    operations = [
        # Create Country model
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    choices=[
                        ('nilfgaard', 'Nilfgaardian Empire'),
                        ('temeria', 'Temeria'),
                        ('redania', 'Redania'),
                        ('skellige', 'Skellige'),
                        ('kovir', 'Kovir and Poviss'),
                        ('cintra', 'Cintra'),
                        ('aedirn', 'Aedirn'),
                        ('kaedwen', 'Kaedwen'),
                        ('lyria', 'Lyria and Rivia'),
                        ('cidaris', 'Cidaris'),
                    ],
                    help_text='Country name',
                    max_length=50,
                    unique=True
                )),
                ('description', models.TextField(blank=True, help_text='Description of the country and its culture')),
                ('bonus_stat', models.CharField(
                    choices=[
                        ('wit', 'Wit'),
                        ('intelligence', 'Intelligence'),
                        ('willpower', 'Willpower'),
                        ('perception', 'Perception'),
                        ('charm', 'Charm'),
                        ('appearance', 'Appearance'),
                        ('graces', 'Graces'),
                        ('cunning', 'Cunning'),
                    ],
                    help_text='Non-physical stat that receives +1 bonus',
                    max_length=20
                )),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
                'ordering': ['name'],
            },
        ),
        # Remove old nation field
        migrations.RemoveField(
            model_name='witchercharacter',
            name='nation',
        ),
        # Add country ForeignKey
        migrations.AddField(
            model_name='witchercharacter',
            name='country',
            field=models.ForeignKey(
                blank=True,
                help_text='Country of origin (provides +1 to a non-physical stat)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='characters',
                to='witcher_rpg.country'
            ),
        ),
        # Populate countries
        migrations.RunPython(populate_countries, reverse_populate_countries),
    ]
