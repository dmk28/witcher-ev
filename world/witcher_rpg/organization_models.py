"""
Organization and Income models for Witcher RPG.

Handles noble houses, witcher schools, trading companies, and passive income.
"""

from django.db import models
from django.core.validators import MinValueValidator
from evennia.objects.models import ObjectDB
from django.utils import timezone
from datetime import timedelta


class OrganizationType(models.TextChoices):
    """Types of organizations in the game."""
    NOBLE_HOUSE = 'noble_house', 'Noble House'
    WITCHER_SCHOOL = 'witcher_school', 'Witcher School'
    TRADING_COMPANY = 'trading_company', 'Trading Company'
    MILITARY_ORDER = 'military_order', 'Military Order'
    MAGICAL_ACADEMY = 'magical_academy', 'Magical Academy'
    CRIMINAL_SYNDICATE = 'criminal_syndicate', 'Criminal Syndicate'
    GUILD = 'guild', 'Professional Guild'
    RELIGIOUS_ORDER = 'religious_order', 'Religious Order'


class Organization(models.Model):
    """
    Represents an organization that characters can join.
    Provides passive income and other benefits.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Organization name"
    )

    organization_type = models.CharField(
        max_length=30,
        choices=OrganizationType.choices,
        help_text="Type of organization"
    )

    description = models.TextField(
        help_text="Description of the organization"
    )

    # Leadership
    leader = models.ForeignKey(
        ObjectDB,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_organizations',
        help_text="Leader/owner of the organization"
    )

    # Treasury
    treasury = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Organization's gold treasury"
    )

    # Investment level (for trading companies)
    investment_level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Investment level (trading companies only)"
    )

    # Income modifiers
    base_income_multiplier = models.FloatField(
        default=1.0,
        help_text="Multiplier for base rank income (e.g., 2.0 for prestigious houses)"
    )

    member_tithe_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Percentage of member income that goes to treasury (0-100)"
    )

    leader_share_percentage = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0)],
        help_text="Percentage of treasury tithing that leader receives (0-100)"
    )

    # Flags
    requires_approval = models.BooleanField(
        default=True,
        help_text="Does joining require leader approval?"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Is this organization currently active?"
    )

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['organization_type', 'name']
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return f"{self.name} ({self.get_organization_type_display()})"

    def get_member_count(self):
        """Get the number of active members."""
        return self.memberships.filter(is_active=True).count()

    def add_to_treasury(self, amount):
        """Add gold to the organization treasury."""
        self.treasury += amount
        self.save()

    def pay_from_treasury(self, amount):
        """
        Pay gold from treasury.

        Returns:
            bool: True if successful, False if insufficient funds
        """
        if self.treasury >= amount:
            self.treasury -= amount
            self.save()
            return True
        return False

    def calculate_leader_income(self):
        """
        Calculate monthly income for the organization leader.

        Returns:
            int: Gold amount
        """
        if not self.leader:
            return 0

        # Get tithing from members
        total_tithing = 0
        for membership in self.memberships.filter(is_active=True).exclude(member=self.leader):
            member_income = membership.calculate_base_income()
            tithe = int(member_income * (self.member_tithe_percentage / 100))
            total_tithing += tithe

        # Leader gets their share of the tithing
        leader_income = int(total_tithing * (self.leader_share_percentage / 100))

        # For trading companies, add investment returns
        if self.organization_type == OrganizationType.TRADING_COMPANY:
            investment_return = self.investment_level * 500  # 500 gold per investment level
            leader_income += investment_return

        return leader_income


class OrganizationMembership(models.Model):
    """
    Links a character to an organization.
    Tracks rank, role, and income.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text="The organization"
    )

    member = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        help_text="The character who is a member"
    )

    # Rank within organization (1-5, same as social rank)
    organization_rank = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Rank within the organization (1-5)"
    )

    # Role/title
    role = models.CharField(
        max_length=100,
        blank=True,
        help_text="Role or title within organization (e.g., 'Guard', 'Master Witcher')"
    )

    # Investment (for trading companies)
    personal_investment = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Personal investment in trading company"
    )

    # Membership status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this membership currently active?"
    )

    is_approved = models.BooleanField(
        default=False,
        help_text="Has this membership been approved by leadership?"
    )

    # Income tracking
    last_income_collection = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time monthly income was collected"
    )

    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['organization', 'member']
        ordering = ['-organization_rank', 'joined_date']
        verbose_name = "Organization Membership"
        verbose_name_plural = "Organization Memberships"

    def __str__(self):
        return f"{self.member.db_key} in {self.organization.name}"

    def calculate_base_income(self):
        """
        Calculate base monthly income from this membership.

        Returns:
            int: Base income in gold
        """
        # Base income per rank
        rank_income = {
            1: 100,    # Rank 1: 100 gold/month
            2: 300,    # Rank 2: 300 gold/month
            3: 800,    # Rank 3: 800 gold/month
            4: 2000,   # Rank 4: 2000 gold/month
            5: 5000,   # Rank 5: 5000 gold/month
        }

        base = rank_income.get(self.organization_rank, 100)

        # Apply organization multiplier
        modified = int(base * self.organization.base_income_multiplier)

        return modified

    def calculate_investment_returns(self):
        """
        Calculate investment returns (trading companies only).

        Returns:
            int: Investment returns in gold
        """
        if self.organization.organization_type != OrganizationType.TRADING_COMPANY:
            return 0

        # 5% return on investment per month
        return int(self.personal_investment * 0.05)

    def calculate_total_income(self):
        """
        Calculate total monthly income from this membership.

        Returns:
            int: Total income in gold
        """
        # Base income
        total = self.calculate_base_income()

        # Investment returns
        total += self.calculate_investment_returns()

        # Subtract tithing (if not the leader)
        if self.member != self.organization.leader:
            tithe = int(total * (self.organization.member_tithe_percentage / 100))
            total -= tithe

        return total

    def can_collect_income(self):
        """
        Check if enough time has passed to collect income.

        Returns:
            tuple: (can_collect, time_remaining_hours)
        """
        if not self.last_income_collection:
            return (True, 0)

        # Income collectable once per 30 days (1 month)
        time_since_last = timezone.now() - self.last_income_collection
        required_wait = timedelta(days=30)

        if time_since_last >= required_wait:
            return (True, 0)
        else:
            remaining = required_wait - time_since_last
            hours_remaining = int(remaining.total_seconds() / 3600)
            return (False, hours_remaining)

    def collect_income(self):
        """
        Collect monthly income.

        Returns:
            tuple: (success, gold_amount, message)
        """
        can_collect, hours_remaining = self.can_collect_income()

        if not can_collect:
            days_remaining = hours_remaining // 24
            return (False, 0, f"You must wait {days_remaining} more days to collect income.")

        if not self.is_active:
            return (False, 0, "This membership is not active.")

        if not self.is_approved and self.organization.requires_approval:
            return (False, 0, "Your membership has not been approved yet.")

        # Calculate income
        income = self.calculate_total_income()

        # Update collection time
        self.last_income_collection = timezone.now()
        self.save()

        # Handle tithing
        if self.member != self.organization.leader:
            base = self.calculate_base_income()
            tithe = int(base * (self.organization.member_tithe_percentage / 100))
            if tithe > 0:
                self.organization.add_to_treasury(tithe)

        return (True, income, "Income collected successfully.")


class IncomeLog(models.Model):
    """
    Logs income collections for auditing.
    """
    character = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='income_logs',
        help_text="Character who collected income"
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='income_logs',
        help_text="Organization income was from (if any)"
    )

    amount = models.IntegerField(
        help_text="Amount of gold collected"
    )

    source = models.CharField(
        max_length=100,
        help_text="Source of income (e.g., 'Rank Stipend', 'Investment Returns')"
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Income Log"
        verbose_name_plural = "Income Logs"

    def __str__(self):
        return f"{self.character.db_key}: {self.amount} gold from {self.source}"
