# Migration to add character advancement system
# Adds AdvancementLog and ApprovalRequest models

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0013_defaultobject_alter_objectdb_id_defaultcharacter_and_more'),
        ('witcher_rpg', '0011_shop_system'),
    ]

    operations = [
        # Create AdvancementLog model
        migrations.CreateModel(
            name='AdvancementLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('advancement_type', models.CharField(
                    choices=[
                        ('stat', 'Stat Increase'),
                        ('skill', 'Skill Increase'),
                    ],
                    help_text='Type of advancement',
                    max_length=20
                )),
                ('stat_or_skill_name', models.CharField(
                    help_text='Name of the stat or skill improved',
                    max_length=50
                )),
                ('old_value', models.IntegerField(
                    help_text='Value before advancement',
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(10)
                    ]
                )),
                ('new_value', models.IntegerField(
                    help_text='Value after advancement',
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(10)
                    ]
                )),
                ('xp_cost', models.IntegerField(
                    help_text='XP spent on this advancement',
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('required_approval', models.BooleanField(
                    default=False,
                    help_text='Whether GM approval was required (levels 6-7)'
                )),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('character', models.ForeignKey(
                    help_text='Character who made the advancement',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='advancements',
                    to='objects.objectdb'
                )),
                ('approved_by', models.ForeignKey(
                    blank=True,
                    help_text='GM who approved this advancement (if required)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='approved_advancements',
                    to='objects.objectdb'
                )),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),

        # Create ApprovalRequest model
        migrations.CreateModel(
            name='ApprovalRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('advancement_type', models.CharField(
                    choices=[
                        ('stat', 'Stat Increase'),
                        ('skill', 'Skill Increase'),
                    ],
                    help_text='Type of advancement',
                    max_length=20
                )),
                ('stat_or_skill_name', models.CharField(
                    help_text='Name of the stat or skill to improve',
                    max_length=50
                )),
                ('current_value', models.IntegerField(
                    help_text='Current value',
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(10)
                    ]
                )),
                ('target_value', models.IntegerField(
                    help_text='Desired new value (must be 6 or 7)',
                    validators=[
                        django.core.validators.MinValueValidator(6),
                        django.core.validators.MaxValueValidator(7)
                    ]
                )),
                ('xp_cost', models.IntegerField(
                    help_text='XP that will be spent upon approval',
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('justification', models.TextField(
                    blank=True,
                    help_text="Player's justification for this advancement"
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending Review'),
                        ('approved', 'Approved'),
                        ('denied', 'Denied'),
                    ],
                    default='pending',
                    help_text='Approval status',
                    max_length=20
                )),
                ('review_notes', models.TextField(
                    blank=True,
                    help_text="GM's notes on approval/denial"
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('character', models.ForeignKey(
                    help_text='Character requesting advancement',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='approval_requests',
                    to='objects.objectdb'
                )),
                ('reviewed_by', models.ForeignKey(
                    blank=True,
                    help_text='GM who reviewed this request',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reviewed_requests',
                    to='objects.objectdb'
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
