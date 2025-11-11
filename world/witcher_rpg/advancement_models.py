"""
Character Advancement Models for Witcher RPG

Tracks character progression through XP spending on stats and skills.

Cost Formula:
- Stats (1-5): New Rating × 10 XP
- Stats (6-7): New Rating × 20 XP (requires GM approval)
- Skills (1-5): New Rating × 5 XP
- Skills (6-7): New Rating × 15 XP (requires GM approval)

Examples:
- Strength 3 → 4: 4 × 10 = 40 XP
- Strength 5 → 6: 6 × 20 = 120 XP (GM approval required)
- Blades 4 → 5: 5 × 5 = 25 XP
- Blades 6 → 7: 7 × 15 = 105 XP (GM approval required)
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB


class AdvancementLog(models.Model):
    """
    Logs all character advancements (stat and skill increases).
    """

    character = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='advancements',
        help_text="Character who made the advancement"
    )

    advancement_type = models.CharField(
        max_length=20,
        choices=[
            ('stat', 'Stat Increase'),
            ('skill', 'Skill Increase'),
        ],
        help_text="Type of advancement"
    )

    stat_or_skill_name = models.CharField(
        max_length=50,
        help_text="Name of the stat or skill improved"
    )

    old_value = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Value before advancement"
    )

    new_value = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Value after advancement"
    )

    xp_cost = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="XP spent on this advancement"
    )

    required_approval = models.BooleanField(
        default=False,
        help_text="Whether GM approval was required (levels 6-7)"
    )

    approved_by = models.ForeignKey(
        ObjectDB,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_advancements',
        help_text="GM who approved this advancement (if required)"
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        approval_note = " (GM Approved)" if self.required_approval else ""
        return (f"{self.character.db_key}: {self.stat_or_skill_name} "
                f"{self.old_value}→{self.new_value} ({self.xp_cost} XP){approval_note}")


class ApprovalRequest(models.Model):
    """
    Tracks pending GM approval requests for high-level advancements (6-7).
    """

    character = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='approval_requests',
        help_text="Character requesting advancement"
    )

    advancement_type = models.CharField(
        max_length=20,
        choices=[
            ('stat', 'Stat Increase'),
            ('skill', 'Skill Increase'),
        ],
        help_text="Type of advancement"
    )

    stat_or_skill_name = models.CharField(
        max_length=50,
        help_text="Name of the stat or skill to improve"
    )

    current_value = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Current value"
    )

    target_value = models.IntegerField(
        validators=[MinValueValidator(6), MaxValueValidator(7)],
        help_text="Desired new value (must be 6 or 7)"
    )

    xp_cost = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="XP that will be spent upon approval"
    )

    justification = models.TextField(
        blank=True,
        help_text="Player's justification for this advancement"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('denied', 'Denied'),
        ],
        default='pending',
        help_text="Approval status"
    )

    reviewed_by = models.ForeignKey(
        ObjectDB,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests',
        help_text="GM who reviewed this request"
    )

    review_notes = models.TextField(
        blank=True,
        help_text="GM's notes on approval/denial"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (f"{self.character.db_key}: {self.stat_or_skill_name} "
                f"{self.current_value}→{self.target_value} [{self.status}]")
