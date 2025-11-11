# Generated manually on 2025-11-11

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("witcher_rpg", "0018_sample_recipes_and_sets"),
        ("objects", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=200,
                        unique=True,
                        help_text="Organization name",
                    ),
                ),
                (
                    "organization_type",
                    models.CharField(
                        max_length=30,
                        choices=[
                            ("noble_house", "Noble House"),
                            ("witcher_school", "Witcher School"),
                            ("trading_company", "Trading Company"),
                            ("military_order", "Military Order"),
                            ("magical_academy", "Magical Academy"),
                            ("criminal_syndicate", "Criminal Syndicate"),
                            ("guild", "Professional Guild"),
                            ("religious_order", "Religious Order"),
                        ],
                        help_text="Type of organization",
                    ),
                ),
                (
                    "description",
                    models.TextField(help_text="Description of the organization"),
                ),
                (
                    "leader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.SET_NULL,
                        null=True,
                        blank=True,
                        related_name="led_organizations",
                        to="objects.objectdb",
                        help_text="Leader/owner of the organization",
                    ),
                ),
                (
                    "treasury",
                    models.IntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        help_text="Organization's gold treasury",
                    ),
                ),
                (
                    "investment_level",
                    models.IntegerField(
                        default=1,
                        validators=[django.core.validators.MinValueValidator(1)],
                        help_text="Investment level (trading companies only)",
                    ),
                ),
                (
                    "base_income_multiplier",
                    models.FloatField(
                        default=1.0,
                        help_text="Multiplier for base rank income (e.g., 2.0 for prestigious houses)",
                    ),
                ),
                (
                    "member_tithe_percentage",
                    models.IntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        help_text="Percentage of member income that goes to treasury (0-100)",
                    ),
                ),
                (
                    "leader_share_percentage",
                    models.IntegerField(
                        default=50,
                        validators=[django.core.validators.MinValueValidator(0)],
                        help_text="Percentage of treasury tithing that leader receives (0-100)",
                    ),
                ),
                (
                    "requires_approval",
                    models.BooleanField(
                        default=True,
                        help_text="Does joining require leader approval?",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Is this organization currently active?",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["organization_type", "name"],
                "verbose_name": "Organization",
                "verbose_name_plural": "Organizations",
            },
        ),
        migrations.CreateModel(
            name="OrganizationMembership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memberships",
                        to="witcher_rpg.organization",
                        help_text="The organization",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organization_memberships",
                        to="objects.objectdb",
                        help_text="The character who is a member",
                    ),
                ),
                (
                    "organization_rank",
                    models.IntegerField(
                        default=1,
                        validators=[django.core.validators.MinValueValidator(1)],
                        help_text="Rank within the organization (1-5)",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        max_length=100,
                        blank=True,
                        help_text="Role or title within organization (e.g., 'Guard', 'Master Witcher')",
                    ),
                ),
                (
                    "personal_investment",
                    models.IntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        help_text="Personal investment in trading company",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Is this membership currently active?",
                    ),
                ),
                (
                    "is_approved",
                    models.BooleanField(
                        default=False,
                        help_text="Has this membership been approved by leadership?",
                    ),
                ),
                (
                    "last_income_collection",
                    models.DateTimeField(
                        null=True,
                        blank=True,
                        help_text="Last time monthly income was collected",
                    ),
                ),
                ("joined_date", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "unique_together": [["organization", "member"]],
                "ordering": ["-organization_rank", "joined_date"],
                "verbose_name": "Organization Membership",
                "verbose_name_plural": "Organization Memberships",
            },
        ),
        migrations.CreateModel(
            name="IncomeLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="income_logs",
                        to="objects.objectdb",
                        help_text="Character who collected income",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        null=True,
                        blank=True,
                        related_name="income_logs",
                        to="witcher_rpg.organization",
                        help_text="Organization income was from (if any)",
                    ),
                ),
                (
                    "amount",
                    models.IntegerField(help_text="Amount of gold collected"),
                ),
                (
                    "source",
                    models.CharField(
                        max_length=100,
                        help_text="Source of income (e.g., 'Rank Stipend', 'Investment Returns')",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-timestamp"],
                "verbose_name": "Income Log",
                "verbose_name_plural": "Income Logs",
            },
        ),
    ]
