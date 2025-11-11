"""
Item and Inventory models for Witcher RPG.
Includes four-tier item system and inventory management.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB


class ItemTier(models.TextChoices):
    """Item tier/rarity levels."""
    TIER_I = 'tier_1', 'Tier I - Common'
    TIER_II = 'tier_2', 'Tier II - Good Crafting'
    TIER_III = 'tier_3', 'Tier III - Exceptional'
    TIER_IV = 'tier_4', 'Tier IV - Relic/Artifact'


class ItemCategory(models.TextChoices):
    """Categories of items."""
    WEAPON = 'weapon', 'Weapon'
    ARMOR = 'armor', 'Armor'
    CONSUMABLE = 'consumable', 'Consumable'
    MATERIAL = 'material', 'Crafting Material'
    QUEST = 'quest', 'Quest Item'
    MISC = 'misc', 'Miscellaneous'


class ItemTemplate(models.Model):
    """
    Template for items that can be instantiated.
    Defines base properties for an item type.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(help_text="Description of the item")

    tier = models.CharField(
        max_length=20,
        choices=ItemTier.choices,
        default=ItemTier.TIER_I,
        help_text="Item tier/rarity"
    )

    category = models.CharField(
        max_length=20,
        choices=ItemCategory.choices,
        default=ItemCategory.MISC,
        help_text="Item category"
    )

    # Value
    gold_value = models.IntegerField(
        default=0,
        help_text="Base gold value"
    )

    # Weight for inventory management
    weight = models.FloatField(
        default=1.0,
        help_text="Weight in units"
    )

    # Stackable items
    is_stackable = models.BooleanField(
        default=False,
        help_text="Can this item stack in inventory?"
    )
    max_stack = models.IntegerField(
        default=1,
        help_text="Maximum stack size"
    )

    # Equipment stats (for weapons/armor)
    damage_bonus = models.IntegerField(default=0, help_text="Damage bonus if weapon")
    armor_value = models.IntegerField(default=0, help_text="Armor value if armor")
    stat_bonuses = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON dict of stat bonuses: {'strength': 2, 'agility': 1}"
    )

    # Special properties for Tier IV items
    special_ability = models.TextField(
        blank=True,
        help_text="Special ability description for relics/artifacts"
    )

    # Crafting
    required_materials = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON dict of materials needed: {'iron_ore': 5, 'leather': 2}"
    )
    crafting_skill_required = models.CharField(
        max_length=50,
        blank=True,
        help_text="Crafting skill required (smithing, carpentry, herbalism)"
    )
    crafting_difficulty = models.IntegerField(
        default=10,
        help_text="Base CR to craft this item (affected by material quality)"
    )

    # Material quality (when used as crafting material)
    material_quality_bonus = models.IntegerField(
        default=0,
        help_text="CR reduction per unit when used as crafting material. Tier I: 0-2, Tier II: 3-7, Tier III: 8-15, Tier IV: 20-35"
    )

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['tier', 'category', 'name']
        verbose_name = "Item Template"
        verbose_name_plural = "Item Templates"

    def __str__(self):
        return f"{self.name} ({self.get_tier_display()})"


class InventoryItem(models.Model):
    """
    An actual item instance in someone's inventory.
    Links to an ItemTemplate for base properties.
    """
    template = models.ForeignKey(
        ItemTemplate,
        on_delete=models.CASCADE,
        related_name='instances',
        help_text="The template this item is based on"
    )

    owner = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        help_text="Who owns this item"
    )

    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity if stackable"
    )

    # Instance-specific properties (for enchanted/modified items)
    custom_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Custom name for this specific item"
    )

    is_equipped = models.BooleanField(
        default=False,
        help_text="Is this item currently equipped?"
    )

    condition = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Item condition (0-100%)"
    )

    # For unique items with modified stats
    custom_bonuses = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom stat bonuses for this specific item"
    )

    acquired_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_equipped', '-template__tier', 'template__name']
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    def __str__(self):
        name = self.custom_name if self.custom_name else self.template.name
        if self.template.is_stackable and self.quantity > 1:
            return f"{name} x{self.quantity}"
        return name

    def get_total_weight(self):
        """Get total weight of this inventory item."""
        return self.template.weight * self.quantity

    def get_stat_bonuses(self):
        """Get all stat bonuses (template + custom)."""
        bonuses = self.template.stat_bonuses.copy() if self.template.stat_bonuses else {}
        if self.custom_bonuses:
            for stat, value in self.custom_bonuses.items():
                bonuses[stat] = bonuses.get(stat, 0) + value
        return bonuses


class BankStorage(models.Model):
    """
    Bank storage for a character or organization.
    Stores gold and items safely.
    """
    owner = models.OneToOneField(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='bank_storage',
        help_text="Character or organization that owns this storage"
    )

    gold_stored = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Gold stored in bank"
    )

    max_storage_slots = models.IntegerField(
        default=100,
        help_text="Maximum number of item stacks that can be stored"
    )

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bank Storage"
        verbose_name_plural = "Bank Storages"

    def __str__(self):
        return f"Bank storage for {self.owner.db_key}"

    def get_stored_items(self):
        """Get all items stored in this bank."""
        return InventoryItem.objects.filter(
            owner=self.owner,
            is_equipped=False
        ).exclude(
            owner__bank_storage__isnull=True
        )

    def get_item_count(self):
        """Get current number of stored item stacks."""
        return self.get_stored_items().count()

    def has_space(self):
        """Check if bank has space for more items."""
        return self.get_item_count() < self.max_storage_slots


class Currency(models.Model):
    """
    Tracks currency (gold) for characters.
    """
    character = models.OneToOneField(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='currency',
        help_text="Character who owns this currency"
    )

    gold = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Gold owned"
    )

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.character.db_key}: {self.gold} gold"
