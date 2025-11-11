# Migration to add social combat/intrigue system
# Adds SocialEncounter, SocialParticipant, and SocialAction models

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


def populate_social_actions(apps, schema_editor):
    """
    Populate default social actions for the intrigue system.
    """
    SocialAction = apps.get_model('witcher_rpg', 'SocialAction')

    actions = [
        # Charm-based attacks
        {
            'name': 'Charm',
            'description': 'Use your natural charisma to win favor and make them more agreeable',
            'action_type': 'attack',
            'primary_stat': 'charm',
            'secondary_stat': 'none',
            'base_difficulty': 20,
            'damage_dice': 3,
            'allowed_stances': ['charming', 'bold'],
            'allowed_encounter_types': ['seduction', 'negotiation', 'manipulation'],
        },
        {
            'name': 'Seduce',
            'description': 'Use appearance and charm to captivate your target romantically',
            'action_type': 'attack',
            'primary_stat': 'appearance',
            'secondary_stat': 'charm',
            'base_difficulty': 25,
            'damage_dice': 4,
            'allowed_stances': ['charming'],
            'allowed_encounter_types': ['seduction'],
        },
        {
            'name': 'Flatter',
            'description': 'Use graceful compliments and appearance to please the target',
            'action_type': 'attack',
            'primary_stat': 'graces',
            'secondary_stat': 'appearance',
            'base_difficulty': 18,
            'damage_dice': 2,
            'allowed_stances': ['charming', 'subtle'],
            'allowed_encounter_types': [],  # Available in all encounter types
        },

        # Cunning-based attacks
        {
            'name': 'Manipulate',
            'description': 'Use cunning to trick and control the target\'s perspective',
            'action_type': 'attack',
            'primary_stat': 'cunning',
            'secondary_stat': 'none',
            'base_difficulty': 22,
            'damage_dice': 3,
            'allowed_stances': ['cunning', 'subtle'],
            'allowed_encounter_types': ['manipulation', 'negotiation', 'debate'],
        },
        {
            'name': 'Undermine',
            'description': 'Use cunning to subtly weaken the target\'s position',
            'action_type': 'undermine',
            'primary_stat': 'cunning',
            'secondary_stat': 'graces',
            'base_difficulty': 20,
            'damage_dice': 2,
            'allowed_stances': ['subtle', 'cunning'],
            'allowed_encounter_types': [],  # Available in all
            'bonus_effects': {'penalty_cr': 5, 'duration': 3},
        },
        {
            'name': 'Deceive',
            'description': 'Use cunning and charm to lie convincingly',
            'action_type': 'attack',
            'primary_stat': 'cunning',
            'secondary_stat': 'charm',
            'base_difficulty': 24,
            'damage_dice': 3,
            'allowed_stances': ['cunning', 'bold'],
            'allowed_encounter_types': ['manipulation', 'negotiation'],
        },

        # Intimidation-based
        {
            'name': 'Intimidate',
            'description': 'Use presence and cunning to cow the opponent into submission',
            'action_type': 'attack',
            'primary_stat': 'charm',
            'secondary_stat': 'cunning',
            'base_difficulty': 20,
            'damage_dice': 3,
            'allowed_stances': ['bold'],
            'allowed_encounter_types': ['intimidation', 'negotiation'],
        },
        {
            'name': 'Threaten',
            'description': 'Make bold threats to break their will',
            'action_type': 'attack',
            'primary_stat': 'cunning',
            'secondary_stat': 'charm',
            'base_difficulty': 22,
            'damage_dice': 4,
            'allowed_stances': ['bold'],
            'allowed_encounter_types': ['intimidation'],
        },

        # Debate-based
        {
            'name': 'Argue',
            'description': 'Use logical arguments to win the debate',
            'action_type': 'attack',
            'primary_stat': 'cunning',
            'secondary_stat': 'none',
            'base_difficulty': 20,
            'damage_dice': 3,
            'allowed_stances': ['bold', 'cunning'],
            'allowed_encounter_types': ['debate', 'negotiation'],
        },

        # Support actions
        {
            'name': 'Compose',
            'description': 'Use graces to regain your composure and restore social capital',
            'action_type': 'support',
            'primary_stat': 'graces',
            'secondary_stat': 'none',
            'base_difficulty': 15,
            'damage_dice': 0,
            'allowed_stances': ['subtle'],
            'allowed_encounter_types': [],  # Available in all
        },
        {
            'name': 'Rally',
            'description': 'Use charm to bolster morale and restore social capital',
            'action_type': 'support',
            'primary_stat': 'charm',
            'secondary_stat': 'none',
            'base_difficulty': 18,
            'damage_dice': 0,
            'allowed_stances': ['charming', 'bold'],
            'allowed_encounter_types': [],  # Available in all
        },

        # Boost actions
        {
            'name': 'Prepare',
            'description': 'Use cunning to set up your next move for bonus dice',
            'action_type': 'boost',
            'primary_stat': 'cunning',
            'secondary_stat': 'none',
            'base_difficulty': 15,
            'damage_dice': 0,
            'allowed_stances': ['subtle', 'cunning'],
            'allowed_encounter_types': [],  # Available in all
            'bonus_effects': {'bonus_dice': 2, 'duration': 1},
        },
    ]

    for action_data in actions:
        SocialAction.objects.create(**action_data)
        print(f"Created social action: {action_data['name']}")


def reverse_populate_social_actions(apps, schema_editor):
    """Remove all social actions."""
    SocialAction = apps.get_model('witcher_rpg', 'SocialAction')
    SocialAction.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0013_defaultobject_alter_objectdb_id_defaultcharacter_and_more'),
        ('witcher_rpg', '0009_social_rank_system'),
    ]

    operations = [
        # Create SocialEncounter model
        migrations.CreateModel(
            name='SocialEncounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Name/description of the social encounter", max_length=200)),
                ('encounter_type', models.CharField(
                    choices=[
                        ('seduction', 'Seduction'),
                        ('negotiation', 'Negotiation'),
                        ('intimidation', 'Intimidation'),
                        ('debate', 'Debate'),
                        ('manipulation', 'Manipulation'),
                    ],
                    default='negotiation',
                    help_text='Type of social encounter affects available actions',
                    max_length=50
                )),
                ('current_round', models.IntegerField(
                    default=1,
                    help_text='Current round of social combat',
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('current_turn_index', models.IntegerField(default=0, help_text='Index of current participant in turn order')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this encounter is still ongoing')),
                ('stakes', models.JSONField(blank=True, default=dict, help_text="What's at stake")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('location', models.ForeignKey(
                    help_text='Where this social encounter is taking place',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='social_encounters',
                    to='objects.objectdb'
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Create SocialParticipant model
        migrations.CreateModel(
            name='SocialParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initiative_roll', models.IntegerField(default=0, help_text='Initiative roll result')),
                ('initiative_order', models.IntegerField(default=0, help_text='Turn order position (lower goes first)')),
                ('current_social_capital', models.IntegerField(
                    default=0,
                    help_text='Current social capital (when 0, participant is defeated)'
                )),
                ('max_social_capital', models.IntegerField(
                    default=0,
                    help_text='Maximum social capital'
                )),
                ('stance', models.CharField(
                    choices=[
                        ('charming', 'Charming - Emphasize appeal and likability'),
                        ('cunning', 'Cunning - Use wit and manipulation'),
                        ('bold', 'Bold - Direct and assertive approach'),
                        ('subtle', 'Subtle - Indirect and measured'),
                    ],
                    default='charming',
                    help_text='Current social stance',
                    max_length=50
                )),
                ('is_active', models.BooleanField(default=True, help_text='Whether this participant is still in the encounter')),
                ('wealth_level', models.IntegerField(
                    choices=[
                        (1, 'Destitute - 10-50 crowns'),
                        (2, 'Poor - 50-200 crowns'),
                        (3, 'Common - 200-1000 crowns'),
                        (4, 'Wealthy - 1000-5000 crowns'),
                        (5, 'Rich - 5000-20000 crowns'),
                        (6, 'Noble - 20000-100000 crowns'),
                        (7, 'Royalty - 100000+ crowns'),
                    ],
                    default=2,
                    help_text='Wealth level determines rewards upon defeat'
                )),
                ('total_damage_dealt', models.IntegerField(default=0, help_text='Total social damage dealt this encounter')),
                ('total_damage_taken', models.IntegerField(default=0, help_text='Total social damage taken this encounter')),
                ('character', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='social_participations',
                    to='objects.objectdb'
                )),
                ('encounter', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='participants',
                    to='witcher_rpg.socialencounter'
                )),
            ],
            options={
                'ordering': ['initiative_order'],
                'unique_together': {('encounter', 'character')},
            },
        ),

        # Create SocialAction model
        migrations.CreateModel(
            name='SocialAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(help_text='What this social action represents')),
                ('action_type', models.CharField(
                    choices=[
                        ('attack', 'Attack - Directly reduce opponent\'s social capital'),
                        ('support', 'Support - Restore ally\'s social capital'),
                        ('undermine', 'Undermine - Apply penalties to opponent'),
                        ('boost', 'Boost - Apply bonuses to self or ally'),
                    ],
                    default='attack',
                    max_length=50
                )),
                ('primary_stat', models.CharField(
                    choices=[
                        ('charm', 'Charm'),
                        ('cunning', 'Cunning'),
                        ('appearance', 'Appearance'),
                        ('graces', 'Graces'),
                    ],
                    help_text='Primary stat used for this action',
                    max_length=20
                )),
                ('secondary_stat', models.CharField(
                    blank=True,
                    choices=[
                        ('none', 'None'),
                        ('charm', 'Charm'),
                        ('cunning', 'Cunning'),
                        ('appearance', 'Appearance'),
                        ('graces', 'Graces'),
                    ],
                    default='none',
                    help_text='Secondary stat (if any) used for this action',
                    max_length=20
                )),
                ('base_difficulty', models.IntegerField(default=20, help_text='Base CR for this action')),
                ('allowed_stances', models.JSONField(
                    blank=True,
                    default=list,
                    help_text='List of stances that can use this action (empty = all)'
                )),
                ('allowed_encounter_types', models.JSONField(
                    blank=True,
                    default=list,
                    help_text='List of encounter types that allow this action (empty = all)'
                )),
                ('damage_dice', models.IntegerField(default=0, help_text='Number of d10s rolled for damage on success')),
                ('bonus_effects', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Additional effects'
                )),
            ],
            options={
                'ordering': ['action_type', 'name'],
            },
        ),

        # Populate default social actions
        migrations.RunPython(populate_social_actions, reverse_populate_social_actions),
    ]
