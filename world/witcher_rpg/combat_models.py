"""
Combat system models for Witcher RPG.
Handles turn-based combat with initiative, stances, attack types, and magic.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB
from .models import WitcherCharacter


class Race(models.Model):
    """
    Character races with special bonuses/penalties.
    """
    RACE_CHOICES = [
        ('human', 'Human'),
        ('elf', 'Elf'),
        ('dwarf', 'Dwarf'),
    ]

    name = models.CharField(
        max_length=50,
        choices=RACE_CHOICES,
        unique=True,
        help_text="The race name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the race"
    )

    # Magic bonuses
    magic_cr_modifier = models.IntegerField(
        default=0,
        help_text="Modifier to spell casting CR (negative is easier)"
    )

    # Combat modifiers
    damage_taken_modifier = models.FloatField(
        default=1.0,
        help_text="Multiplier for damage taken (1.0 is normal, >1.0 takes more damage)"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Race"
        verbose_name_plural = "Races"

    def __str__(self):
        return self.get_name_display()


class WitcherStyle(models.Model):
    """
    Witcher fighting styles from Witcher 3.
    """
    STYLE_CHOICES = [
        ('cat', 'School of the Cat'),
        ('viper', 'School of the Viper'),
        ('bear', 'School of the Bear'),
        ('eagle', 'School of the Eagle'),
        ('dragon', 'School of the Dragon'),
        ('basilisk', 'School of the Basilisk'),
    ]

    name = models.CharField(
        max_length=50,
        choices=STYLE_CHOICES,
        unique=True,
        help_text="The Witcher school/style name"
    )
    description = models.TextField(
        help_text="Description of the fighting style"
    )

    # Style bonuses
    agility_bonus = models.IntegerField(default=0)
    reflexes_bonus = models.IntegerField(default=0)
    strength_bonus = models.IntegerField(default=0)
    endurance_bonus = models.IntegerField(default=0)
    perception_bonus = models.IntegerField(default=0)

    # Special abilities
    special_ability = models.TextField(
        blank=True,
        help_text="Special ability granted by this style"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Witcher Style"
        verbose_name_plural = "Witcher Styles"

    def __str__(self):
        return self.get_name_display()


class MagicElement(models.Model):
    """
    Magic elements for spell casting.
    """
    ELEMENT_CHOICES = [
        ('fire', 'Fire'),
        ('ice', 'Ice'),
        ('lightning', 'Lightning'),
        ('earth', 'Earth'),
        ('wind', 'Wind'),
        ('arcane', 'Arcane'),
    ]

    name = models.CharField(
        max_length=50,
        choices=ELEMENT_CHOICES,
        unique=True
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Magic Element"
        verbose_name_plural = "Magic Elements"

    def __str__(self):
        return self.get_name_display()


class CombatEncounter(models.Model):
    """
    Tracks an active combat encounter.
    """
    name = models.CharField(
        max_length=200,
        help_text="Name/description of this combat encounter"
    )
    location = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='combat_encounters',
        help_text="The room where combat is taking place"
    )
    current_round = models.IntegerField(
        default=1,
        help_text="Current combat round"
    )
    current_turn_index = models.IntegerField(
        default=0,
        help_text="Index of the current participant's turn"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this combat is still ongoing"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Combat Encounter"
        verbose_name_plural = "Combat Encounters"

    def __str__(self):
        return f"{self.name} (Round {self.current_round})"


class CombatParticipant(models.Model):
    """
    Tracks a participant in combat.
    """
    STANCE_CHOICES = [
        ('defensive', 'Defensive'),
        ('moderate', 'Moderate'),
        ('offensive', 'Offensive'),
    ]

    ATTACK_TYPE_CHOICES = [
        ('light', 'Light Attack'),
        ('standard', 'Standard Attack'),
        ('heavy', 'Heavy Attack'),
    ]

    encounter = models.ForeignKey(
        CombatEncounter,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    character = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        help_text="The character participating in combat"
    )

    # Initiative
    initiative_roll = models.IntegerField(
        default=0,
        help_text="Initiative roll (Reflexes + Perception + 1d10)"
    )
    initiative_order = models.IntegerField(
        default=0,
        help_text="Turn order (lower goes first)"
    )

    # Combat state
    current_hp = models.IntegerField(
        default=100,
        help_text="Current hit points"
    )
    max_hp = models.IntegerField(
        default=100,
        help_text="Maximum hit points"
    )

    stance = models.CharField(
        max_length=20,
        choices=STANCE_CHOICES,
        default='moderate',
        help_text="Current combat stance"
    )

    last_attack_type = models.CharField(
        max_length=20,
        choices=ATTACK_TYPE_CHOICES,
        default='standard',
        help_text="Last attack type used"
    )

    recovery_penalty = models.IntegerField(
        default=0,
        help_text="Current penalty from recovery (frame disadvantage)"
    )

    # Spell casting state
    is_casting = models.BooleanField(
        default=False,
        help_text="Currently casting a spell"
    )
    spell_turns_remaining = models.IntegerField(
        default=0,
        help_text="Turns remaining before spell is cast"
    )
    spell_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of spell being cast"
    )
    spell_difficulty = models.CharField(
        max_length=20,
        blank=True,
        help_text="Difficulty level of spell being cast"
    )
    spell_element = models.CharField(
        max_length=50,
        blank=True,
        help_text="Element of spell being cast"
    )

    # Equipment
    armor_value = models.IntegerField(
        default=0,
        help_text="Armor value for damage reduction"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this participant is still in combat (not dead/fled)"
    )

    class Meta:
        ordering = ['initiative_order']
        verbose_name = "Combat Participant"
        verbose_name_plural = "Combat Participants"

    def __str__(self):
        return f"{self.character.name} in {self.encounter.name}"

    def get_stance_bonuses(self):
        """
        Get the bonuses/penalties from current stance.

        Returns:
            dict: Bonuses for attack, defense, and CR modifiers
        """
        if self.stance == 'defensive':
            return {
                'reflexes_defense': 5,
                'attack_cr_modifier': 10,
                'defense_cr_modifier': 0
            }
        elif self.stance == 'offensive':
            return {
                'agility_attack': 5,
                'attack_cr_modifier': 0,
                'defense_cr_modifier': 10
            }
        else:  # moderate
            return {
                'attack_cr_modifier': 0,
                'defense_cr_modifier': 0
            }

    def get_attack_frame_data(self):
        """
        Get the recovery and modifiers for the last attack type.

        Returns:
            dict: Recovery value, malus, and damage modifier
        """
        frames = {
            'light': {
                'recovery': 10,
                'malus': 0,
                'damage_modifier': -0.5,
                'description': 'Quick but weak'
            },
            'standard': {
                'recovery': 8,
                'malus': -2,
                'damage_modifier': 0,
                'description': 'Balanced attack'
            },
            'heavy': {
                'recovery': 4,
                'malus': -6,
                'damage_modifier': 0.5,
                'description': 'Slow but powerful'
            }
        }
        return frames.get(self.last_attack_type, frames['standard'])
