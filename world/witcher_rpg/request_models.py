"""
Unified Request System for Witcher RPG

Handles all types of GM approval requests:
- Character generation/creation
- Advancement requests (stats/skills 6-7)
- Special requests (custom items, plot hooks, etc)
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB
from django.utils import timezone


class UnifiedRequest(models.Model):
    """
    Master request model for all GM approval workflows.

    This replaces the old ApprovalRequest and adds character generation requests.
    """

    # Request identification
    requestor = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='submitted_requests',
        help_text="Player/character who submitted the request"
    )

    request_type = models.CharField(
        max_length=50,
        choices=[
            ('chargen', 'Character Generation'),
            ('advancement_stat', 'Stat Advancement (6-7)'),
            ('advancement_skill', 'Skill Advancement (6-7)'),
            ('special_item', 'Special Item Request'),
            ('plot_hook', 'Plot Hook Request'),
            ('custom', 'Custom Request'),
        ],
        help_text="Type of request"
    )

    # Request details
    title = models.CharField(
        max_length=200,
        help_text="Brief title of the request"
    )

    description = models.TextField(
        help_text="Detailed description and justification"
    )

    request_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured data for the request (character stats, advancement details, etc)"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('denied', 'Denied'),
            ('revoked', 'Revoked by Requester'),
        ],
        default='pending',
        help_text="Current status"
    )

    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('normal', 'Normal'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='normal',
        help_text="Priority level"
    )

    # Review info
    reviewed_by = models.ForeignKey(
        ObjectDB,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_unified_requests',
        help_text="GM who reviewed this request"
    )

    review_notes = models.TextField(
        blank=True,
        help_text="GM's notes on approval/denial"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'request_type']),
            models.Index(fields=['requestor', 'status']),
        ]

    def __str__(self):
        return f"{self.get_request_type_display()}: {self.title} [{self.status}]"

    def approve(self, gm, notes=""):
        """Mark request as approved."""
        self.status = 'approved'
        self.reviewed_by = gm
        self.review_notes = notes
        self.reviewed_at = timezone.now()
        self.save()

    def deny(self, gm, reason):
        """Mark request as denied."""
        self.status = 'denied'
        self.reviewed_by = gm
        self.review_notes = reason
        self.reviewed_at = timezone.now()
        self.save()

    def revoke(self):
        """Requester withdraws their request."""
        self.status = 'revoked'
        self.reviewed_at = timezone.now()
        self.save()


class CharacterGenerationRequest(models.Model):
    """
    Specific model for character generation requests.

    Links to UnifiedRequest for workflow, contains character creation data.
    """

    unified_request = models.OneToOneField(
        UnifiedRequest,
        on_delete=models.CASCADE,
        related_name='chargen_details',
        help_text="Link to unified request"
    )

    # Character concept
    character_name = models.CharField(
        max_length=200,
        help_text="Proposed character name"
    )

    vocation = models.ForeignKey(
        'Vocation',
        on_delete=models.CASCADE,
        help_text="Chosen vocation"
    )

    race = models.CharField(
        max_length=50,
        help_text="Character race"
    )

    country = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Country of origin"
    )

    social_rank = models.IntegerField(
        choices=[
            (1, 'Rank 1 - Outcast'),
            (2, 'Rank 2 - Commoner'),
            (3, 'Rank 3 - Knight/Small Gentry'),
            (4, 'Rank 4 - Landed Gentry'),
            (5, 'Rank 5 - Royalty'),
        ],
        default=2,
        help_text="Social rank"
    )

    # Stats allocation
    stats_allocation = models.JSONField(
        help_text="Proposed stat allocation: {'strength': 3, 'agility': 4, ...}"
    )

    skills_allocation = models.JSONField(
        help_text="Proposed skill allocation: {'blades': 4, 'alchemy': 2, ...}"
    )

    # Background
    background = models.TextField(
        help_text="Character background and concept"
    )

    # Physical description
    physical_description = models.TextField(
        blank=True,
        help_text="Character physical appearance"
    )

    # Validation flags
    stats_valid = models.BooleanField(
        default=False,
        help_text="Whether stat allocation is mechanically valid"
    )

    skills_valid = models.BooleanField(
        default=False,
        help_text="Whether skill allocation is mechanically valid"
    )

    validation_errors = models.JSONField(
        default=list,
        blank=True,
        help_text="List of validation errors if any"
    )

    class Meta:
        ordering = ['-unified_request__created_at']

    def __str__(self):
        return f"CharGen: {self.character_name} ({self.vocation.name})"

    def validate_allocations(self):
        """
        Validate stat and skill allocations against game rules.

        Returns:
            tuple: (is_valid, errors list)
        """
        from world.witcher_rpg.models import WitcherCharacter

        errors = []

        # Validate stats
        stat_valid, stat_error = WitcherCharacter.validate_stat_allocation(
            self.stats_allocation
        )
        if not stat_valid:
            errors.append(f"Stats: {stat_error}")

        # Validate skills
        skill_valid, skill_error = WitcherCharacter.validate_skill_allocation(
            self.skills_allocation
        )
        if not skill_valid:
            errors.append(f"Skills: {skill_error}")

        # Validate social rank for vocation
        max_rank = WitcherCharacter.get_max_rank_for_vocation(self.vocation.name)
        if self.social_rank > max_rank:
            errors.append(
                f"Social rank {self.social_rank} exceeds maximum {max_rank} "
                f"for {self.vocation.name}"
            )

        self.stats_valid = stat_valid
        self.skills_valid = skill_valid
        self.validation_errors = errors
        self.save()

        return (len(errors) == 0, errors)
