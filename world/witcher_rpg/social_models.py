"""
Social Combat Models for Witcher RPG

This module implements the Intrigue system - social combat where characters
use charm, cunning, appearance, and graces to undermine opponents' social capital
and convert victories into material gains (gold, favors, rare items).

Examples:
- Dandelion seducing patronesses for gold and luxury items
- Merchants negotiating better trade deals
- Nobles intimidating commoners for information
- Courtesans manipulating targets for secrets and wealth
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB


class SocialEncounter(models.Model):
    """
    Represents an ongoing social combat/intrigue encounter.

    Social combat uses charm, cunning, appearance, and graces instead of
    physical stats. Victory allows converting social capital into rewards.
    """

    name = models.CharField(
        max_length=200,
        help_text="Name/description of the social encounter (e.g., 'Seduction at the Ball')"
    )

    location = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='social_encounters',
        help_text="Where this social encounter is taking place"
    )

    encounter_type = models.CharField(
        max_length=50,
        choices=[
            ('seduction', 'Seduction'),
            ('negotiation', 'Negotiation'),
            ('intimidation', 'Intimidation'),
            ('debate', 'Debate'),
            ('manipulation', 'Manipulation'),
        ],
        default='negotiation',
        help_text="Type of social encounter affects available actions"
    )

    current_round = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Current round of social combat"
    )

    current_turn_index = models.IntegerField(
        default=0,
        help_text="Index of current participant in turn order"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this encounter is still ongoing"
    )

    stakes = models.JSONField(
        default=dict,
        blank=True,
        help_text="What's at stake: {'gold': 1000, 'item': 'rare_perfume', 'favor': 'introduction_to_duke'}"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = "Active" if self.is_active else "Ended"
        return f"{self.name} ({status})"

    def get_current_participant(self):
        """Get the participant whose turn it is."""
        participants = self.participants.filter(is_active=True).order_by('initiative_order')
        if participants.exists() and 0 <= self.current_turn_index < participants.count():
            return participants[self.current_turn_index]
        return None

    def advance_turn(self):
        """Move to next participant's turn."""
        participants = self.participants.filter(is_active=True).order_by('initiative_order')
        count = participants.count()

        if count == 0:
            return

        self.current_turn_index += 1

        # If we've gone through all participants, start new round
        if self.current_turn_index >= count:
            self.current_turn_index = 0
            self.current_round += 1

        self.save()


class SocialParticipant(models.Model):
    """
    Represents a participant in social combat.

    Social Capital represents a character's standing and influence in the encounter.
    When reduced to 0, the character is "defeated" socially.
    """

    encounter = models.ForeignKey(
        SocialEncounter,
        on_delete=models.CASCADE,
        related_name='participants'
    )

    character = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='social_participations'
    )

    # Initiative
    initiative_roll = models.IntegerField(
        default=0,
        help_text="Initiative roll result"
    )

    initiative_order = models.IntegerField(
        default=0,
        help_text="Turn order position (lower goes first)"
    )

    # Social Capital (like HP in physical combat)
    current_social_capital = models.IntegerField(
        default=0,
        help_text="Current social capital (when 0, participant is defeated)"
    )

    max_social_capital = models.IntegerField(
        default=0,
        help_text="Maximum social capital (Charm + Cunning + Appearance + Graces) × multiplier"
    )

    # Stance affects available actions and modifiers
    stance = models.CharField(
        max_length=50,
        choices=[
            ('charming', 'Charming - Emphasize appeal and likability'),
            ('cunning', 'Cunning - Use wit and manipulation'),
            ('bold', 'Bold - Direct and assertive approach'),
            ('subtle', 'Subtle - Indirect and measured'),
        ],
        default='charming',
        help_text="Current social stance"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this participant is still in the encounter"
    )

    # Wealth for reward conversion
    wealth_level = models.IntegerField(
        default=2,
        choices=[
            (1, 'Destitute - 10-50 crowns'),
            (2, 'Poor - 50-200 crowns'),
            (3, 'Common - 200-1000 crowns'),
            (4, 'Wealthy - 1000-5000 crowns'),
            (5, 'Rich - 5000-20000 crowns'),
            (6, 'Noble - 20000-100000 crowns'),
            (7, 'Royalty - 100000+ crowns'),
        ],
        help_text="Wealth level determines rewards upon defeat"
    )

    # Tracking
    total_damage_dealt = models.IntegerField(
        default=0,
        help_text="Total social damage dealt this encounter"
    )

    total_damage_taken = models.IntegerField(
        default=0,
        help_text="Total social damage taken this encounter"
    )

    class Meta:
        ordering = ['initiative_order']
        unique_together = ['encounter', 'character']

    def __str__(self):
        return f"{self.character.db_key} in {self.encounter.name}"

    def take_social_damage(self, amount):
        """
        Reduce social capital by damage amount.
        Returns actual damage taken (may be less if capital drops to 0).
        """
        actual_damage = min(amount, self.current_social_capital)
        self.current_social_capital = max(0, self.current_social_capital - amount)
        self.total_damage_taken += actual_damage

        if self.current_social_capital <= 0:
            self.is_active = False

        self.save()
        return actual_damage

    def restore_social_capital(self, amount):
        """Restore social capital (from support actions, etc.)."""
        old_capital = self.current_social_capital
        self.current_social_capital = min(
            self.max_social_capital,
            self.current_social_capital + amount
        )
        self.save()
        return self.current_social_capital - old_capital

    def calculate_reward_value(self, victory_margin=0):
        """
        Calculate reward value based on wealth level and victory margin.

        Returns dict with gold and potential items.
        """
        # Base gold by wealth level
        wealth_ranges = {
            1: (10, 50),
            2: (50, 200),
            3: (200, 1000),
            4: (1000, 5000),
            5: (5000, 20000),
            6: (20000, 100000),
            7: (100000, 500000),
        }

        min_gold, max_gold = wealth_ranges.get(self.wealth_level, (100, 500))

        # Victory margin affects percentage of wealth extracted
        # Marginal victory (0-20): 10-30% of wealth
        # Solid victory (21-50): 30-50% of wealth
        # Decisive victory (51+): 50-80% of wealth
        if victory_margin <= 20:
            percentage = 0.10 + (victory_margin / 20) * 0.20
        elif victory_margin <= 50:
            percentage = 0.30 + ((victory_margin - 20) / 30) * 0.20
        else:
            percentage = 0.50 + min((victory_margin - 50) / 50, 1.0) * 0.30

        # Calculate gold reward
        base_gold = (min_gold + max_gold) / 2
        gold_reward = int(base_gold * percentage)

        # Higher wealth levels and better victories grant rare items
        item_chance = None
        if self.wealth_level >= 4 and victory_margin > 30:
            item_chance = 'common_luxury'
        if self.wealth_level >= 5 and victory_margin > 50:
            item_chance = 'rare_luxury'
        if self.wealth_level >= 6 and victory_margin > 70:
            item_chance = 'noble_gift'

        return {
            'gold': gold_reward,
            'item_tier': item_chance,
            'favor_level': min(victory_margin // 25, 3)  # 0-3 favor levels
        }


class SocialAction(models.Model):
    """
    Defines available social actions (like attacks in combat).

    Different encounter types and stances enable different actions.
    """

    name = models.CharField(max_length=100, unique=True)

    description = models.TextField(
        help_text="What this social action represents"
    )

    action_type = models.CharField(
        max_length=50,
        choices=[
            ('attack', 'Attack - Directly reduce opponent\'s social capital'),
            ('support', 'Support - Restore ally\'s social capital'),
            ('undermine', 'Undermine - Apply penalties to opponent'),
            ('boost', 'Boost - Apply bonuses to self or ally'),
        ],
        default='attack'
    )

    # Which stats are used for this action
    primary_stat = models.CharField(
        max_length=20,
        choices=[
            ('charm', 'Charm'),
            ('cunning', 'Cunning'),
            ('appearance', 'Appearance'),
            ('graces', 'Graces'),
        ],
        help_text="Primary stat used for this action"
    )

    secondary_stat = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('charm', 'Charm'),
            ('cunning', 'Cunning'),
            ('appearance', 'Appearance'),
            ('graces', 'Graces'),
        ],
        default='none',
        blank=True,
        help_text="Secondary stat (if any) used for this action"
    )

    base_difficulty = models.IntegerField(
        default=20,
        help_text="Base CR for this action"
    )

    # Restrictions
    allowed_stances = models.JSONField(
        default=list,
        blank=True,
        help_text="List of stances that can use this action (empty = all)"
    )

    allowed_encounter_types = models.JSONField(
        default=list,
        blank=True,
        help_text="List of encounter types that allow this action (empty = all)"
    )

    # Effects
    damage_dice = models.IntegerField(
        default=0,
        help_text="Number of d10s rolled for damage on success"
    )

    bonus_effects = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional effects: {'penalty_cr': 5, 'bonus_dice': 2, 'duration': 3}"
    )

    class Meta:
        ordering = ['action_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_action_type_display()})"

    def can_use_in_encounter(self, encounter_type, stance):
        """Check if this action can be used given encounter type and stance."""
        # Check encounter type restriction
        if self.allowed_encounter_types and encounter_type not in self.allowed_encounter_types:
            return False

        # Check stance restriction
        if self.allowed_stances and stance not in self.allowed_stances:
            return False

        return True
