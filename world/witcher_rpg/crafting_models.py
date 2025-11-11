"""
Advanced Crafting Models for Witcher RPG

Implements recipe-based crafting for tier III-IV items and set item system
with bonuses for wearing multiple pieces.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB


class CraftingRecipe(models.Model):
    """
    Defines how to craft high-tier (III-IV) items.

    Recipes are learned through training, quests, or discovery.
    Only characters with the recipe can attempt to craft the item.
    """

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of the recipe (e.g., 'Moonblade Silver Sword Formula')"
    )

    result_item = models.ForeignKey(
        'ItemTemplate',
        on_delete=models.CASCADE,
        related_name='crafting_recipes',
        null=True,
        blank=True,
        help_text="Item produced by this recipe (optional until item is created)"
    )

    crafting_type = models.CharField(
        max_length=50,
        choices=[
            ('weaponsmithing', 'Weaponsmithing'),
            ('armorsmithing', 'Armorsmithing'),
            ('alchemy', 'Alchemy'),
            ('runecrafting', 'Runecrafting'),
            ('jewelcrafting', 'Jewelcrafting'),
            ('tailoring', 'Tailoring'),
        ],
        help_text="Type of crafting required"
    )

    min_skill_level = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Minimum crafting skill level required"
    )

    base_difficulty = models.IntegerField(
        default=50,
        validators=[MinValueValidator(10), MaxValueValidator(150)],
        help_text="Base CR for crafting attempt (materials reduce this)"
    )

    # Requirements
    required_materials = models.JSONField(
        default=dict,
        help_text="Materials needed: {'steel_ingot': 5, 'silver_dust': 2}"
    )

    required_workshop = models.CharField(
        max_length=50,
        choices=[
            ('forge', 'Forge - Metalworking'),
            ('laboratory', 'Laboratory - Alchemy'),
            ('enchanting_table', 'Enchanting Table - Magic'),
            ('workshop', 'Workshop - General crafting'),
            ('tailor_station', 'Tailor Station - Clothing'),
        ],
        help_text="Workshop type required"
    )

    time_required_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        help_text="Real-world minutes required to craft (or in-game time)"
    )

    # Rewards and costs
    xp_reward = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0)],
        help_text="XP gained on successful craft"
    )

    gold_cost = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Gold cost to use the recipe (workshop fees, etc)"
    )

    # Discovery and learning
    is_rare = models.BooleanField(
        default=False,
        help_text="Rare recipes are harder to find"
    )

    discovery_location = models.TextField(
        blank=True,
        help_text="Lore about where this recipe can be found"
    )

    # Set item connection
    set_piece = models.ForeignKey(
        'ItemSet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipes',
        help_text="If this item is part of a set"
    )

    class Meta:
        ordering = ['crafting_type', 'min_skill_level', 'name']

    def __str__(self):
        return f"{self.name} (Skill {self.min_skill_level}+, CR {self.base_difficulty})"

    def calculate_adjusted_difficulty(self, materials_quality):
        """
        Calculate final CR based on material quality.

        Args:
            materials_quality: Average quality/tier of materials used

        Returns:
            int: Adjusted difficulty
        """
        # Better materials reduce difficulty
        reduction = (materials_quality - 1) * 10  # Tier II = -10, Tier III = -20, etc
        return max(10, self.base_difficulty - reduction)


class ItemSet(models.Model):
    """
    Defines a set of items that provide bonuses when worn together.

    Examples:
    - Witcher Gear (Cat School, Wolf School, etc)
    - Legendary Armor Sets
    - Enchanted Jewelry Collections
    """

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of the set (e.g., 'Cat School Witcher Gear')"
    )

    description = models.TextField(
        help_text="Lore and description of the set"
    )

    set_type = models.CharField(
        max_length=50,
        choices=[
            ('armor', 'Armor Set'),
            ('weapons', 'Weapon Set'),
            ('jewelry', 'Jewelry Set'),
            ('mixed', 'Mixed Set'),
        ],
        default='armor',
        help_text="Type of set"
    )

    tier = models.IntegerField(
        choices=[
            (1, 'Tier I'),
            (2, 'Tier II'),
            (3, 'Tier III'),
            (4, 'Tier IV'),
        ],
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="Set tier (usually III or IV)"
    )

    # Set bonuses at different piece counts
    two_piece_bonus = models.JSONField(
        default=dict,
        blank=True,
        help_text="Bonus for wearing 2 pieces: {'stat': 'agility', 'value': 1}"
    )

    three_piece_bonus = models.JSONField(
        default=dict,
        blank=True,
        help_text="Bonus for wearing 3 pieces"
    )

    four_piece_bonus = models.JSONField(
        default=dict,
        blank=True,
        help_text="Bonus for wearing 4 pieces"
    )

    five_piece_bonus = models.JSONField(
        default=dict,
        blank=True,
        help_text="Bonus for wearing 5+ pieces"
    )

    class Meta:
        ordering = ['tier', 'name']

    def __str__(self):
        return f"{self.name} (Tier {self.tier})"

    def get_bonus_for_pieces(self, piece_count):
        """
        Get the active bonus based on number of pieces worn.

        Returns:
            dict: Combined bonuses from all thresholds met
        """
        bonuses = {}

        if piece_count >= 2 and self.two_piece_bonus:
            bonuses.update(self.two_piece_bonus)

        if piece_count >= 3 and self.three_piece_bonus:
            bonuses.update(self.three_piece_bonus)

        if piece_count >= 4 and self.four_piece_bonus:
            bonuses.update(self.four_piece_bonus)

        if piece_count >= 5 and self.five_piece_bonus:
            bonuses.update(self.five_piece_bonus)

        return bonuses


class LearnedRecipe(models.Model):
    """
    Tracks which recipes a character has learned.
    """

    character = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='learned_recipes',
        help_text="Character who learned the recipe"
    )

    recipe = models.ForeignKey(
        CraftingRecipe,
        on_delete=models.CASCADE,
        related_name='learned_by',
        help_text="Recipe learned"
    )

    learned_date = models.DateTimeField(auto_now_add=True)

    times_crafted = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of times this character has crafted this recipe"
    )

    class Meta:
        unique_together = ['character', 'recipe']
        ordering = ['-learned_date']

    def __str__(self):
        return f"{self.character.db_key} knows {self.recipe.name}"


class CraftingAttempt(models.Model):
    """
    Logs crafting attempts (successes and failures).
    """

    character = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='crafting_attempts',
        help_text="Character who attempted crafting"
    )

    recipe = models.ForeignKey(
        CraftingRecipe,
        on_delete=models.CASCADE,
        related_name='attempts',
        help_text="Recipe attempted"
    )

    success = models.BooleanField(
        help_text="Whether the crafting succeeded"
    )

    roll_result = models.IntegerField(
        help_text="Dice roll result"
    )

    difficulty = models.IntegerField(
        help_text="CR that was rolled against"
    )

    materials_used = models.JSONField(
        default=dict,
        help_text="Materials consumed in the attempt"
    )

    xp_gained = models.IntegerField(
        default=0,
        help_text="XP gained (only on success)"
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        status = "Success" if self.success else "Failure"
        return f"{self.character.db_key} - {self.recipe.name} ({status})"


class VocationSkillCostMultiplier(models.Model):
    """
    Defines XP cost multipliers for skills based on vocation.

    This rewards specialists - artisans pay less to advance crafting,
    warriors pay less for combat skills, etc.

    Default multiplier is 1.0 (normal cost).
    Specialists get 0.5-0.75 (half to 3/4 cost).
    Non-specialists may get 1.5-2.0 (1.5x to 2x cost).
    """

    vocation = models.ForeignKey(
        'Vocation',
        on_delete=models.CASCADE,
        related_name='skill_multipliers',
        help_text="Vocation these multipliers apply to"
    )

    skill_name = models.CharField(
        max_length=50,
        help_text="Name of the skill"
    )

    multiplier = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(5.0)],
        help_text="XP cost multiplier (0.5 = half cost, 2.0 = double cost)"
    )

    class Meta:
        unique_together = ['vocation', 'skill_name']
        ordering = ['vocation', 'skill_name']

    def __str__(self):
        return f"{self.vocation.name} - {self.skill_name}: {self.multiplier}x"

    @staticmethod
    def get_multiplier(vocation, skill_name):
        """
        Get XP cost multiplier for a vocation/skill combination.

        Returns:
            float: Multiplier (1.0 if not defined)
        """
        try:
            multiplier_obj = VocationSkillCostMultiplier.objects.get(
                vocation=vocation,
                skill_name=skill_name
            )
            return multiplier_obj.multiplier
        except VocationSkillCostMultiplier.DoesNotExist:
            return 1.0  # Default: normal cost
