"""
Shop System Models for Witcher RPG

Implements a comprehensive shop system where:
- Players can own shops and sell items
- NPCs run shops and are susceptible to social combat
- Shops automatically restock based on type, tier, and faction
- Different shop types (weaponsmith, armorsmith, jeweler, etc.)
- Tier-based investment determines quality and quantity
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB
import random


class Shop(models.Model):
    """
    Represents a shop in the game world.

    Shops are owned by players or NPCs, run by merchant NPCs, and
    automatically restock based on their type, tier, and faction.
    """

    name = models.CharField(
        max_length=200,
        help_text="Name of the shop (e.g., 'The Steel & Silver', 'Elegant Armaments')"
    )

    location = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='shops',
        help_text="Room where this shop is located"
    )

    owner = models.ForeignKey(
        ObjectDB,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_shops',
        help_text="Player or NPC who owns this shop"
    )

    merchant = models.ForeignKey(
        ObjectDB,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merchant_shops',
        help_text="NPC merchant who runs the shop (susceptible to social combat)"
    )

    shop_type = models.CharField(
        max_length=50,
        choices=[
            ('weaponsmith', 'Weaponsmith - Swords, axes, crossbows'),
            ('armorsmith', 'Armorsmith - Armor and protective gear'),
            ('jeweler', 'Jeweler - Jewelry, gems, luxury items'),
            ('alchemist', 'Alchemist - Potions, oils, ingredients'),
            ('general', 'General Store - Basic supplies and consumables'),
            ('tailor', 'Tailor - Clothing and fashion'),
            ('blacksmith', 'Blacksmith - Tools and basic weapons'),
            ('enchanter', 'Enchanter - Magical items and scrolls'),
        ],
        help_text="Type of shop determines what items are stocked"
    )

    tier = models.IntegerField(
        choices=[
            (1, 'Tier I - Poor quality, basic items'),
            (2, 'Tier II - Common quality, decent selection'),
            (3, 'Tier III - Good quality, wide selection'),
            (4, 'Tier IV - Excellent quality, rare items'),
        ],
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="Investment tier determines quality and quantity of stock"
    )

    faction = models.CharField(
        max_length=50,
        choices=[
            ('independent', 'Independent'),
            ('nilfgaard', 'Nilfgaardian Empire'),
            ('temeria', 'Temeria'),
            ('redania', 'Redania'),
            ('skellige', 'Skellige'),
            ('witcher', 'Witcher Guild'),
            ('mage', 'Mage Conclave'),
            ('merchant_guild', 'Merchant Guild'),
        ],
        default='independent',
        help_text="Faction affiliation affects available items"
    )

    # Financial
    gold_reserves = models.IntegerField(
        default=1000,
        validators=[MinValueValidator(0)],
        help_text="Gold available for buying items from players"
    )

    markup_percentage = models.IntegerField(
        default=150,
        validators=[MinValueValidator(100), MaxValueValidator(500)],
        help_text="Sell price as percentage of base value (150 = 50% markup)"
    )

    buyback_percentage = models.IntegerField(
        default=50,
        validators=[MinValueValidator(10), MaxValueValidator(100)],
        help_text="Buy price as percentage of base value (50 = buy at half price)"
    )

    # Restocking
    last_restock = models.DateTimeField(
        auto_now_add=True,
        help_text="When the shop was last restocked"
    )

    restock_interval_hours = models.IntegerField(
        default=24,
        validators=[MinValueValidator(1)],
        help_text="Hours between automatic restocks"
    )

    # Status
    is_open = models.BooleanField(
        default=True,
        help_text="Whether the shop is currently open for business"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'location']

    def __str__(self):
        return f"{self.name} ({self.get_shop_type_display()}) - Tier {self.tier}"

    def get_restock_quantity(self):
        """
        Get number of items to stock based on tier.
        """
        base_quantities = {
            1: (3, 8),    # Tier I: 3-8 items
            2: (8, 15),   # Tier II: 8-15 items
            3: (15, 25),  # Tier III: 15-25 items
            4: (25, 40),  # Tier IV: 25-40 items
        }
        min_qty, max_qty = base_quantities.get(self.tier, (5, 10))
        return random.randint(min_qty, max_qty)

    def calculate_sell_price(self, base_value):
        """Calculate price to sell item to player."""
        return int(base_value * (self.markup_percentage / 100))

    def calculate_buy_price(self, base_value):
        """Calculate price to buy item from player."""
        return int(base_value * (self.buyback_percentage / 100))

    def can_afford(self, amount):
        """Check if shop has enough gold to buy from player."""
        return self.gold_reserves >= amount

    def pay_gold(self, amount):
        """Deduct gold from shop reserves."""
        if self.can_afford(amount):
            self.gold_reserves -= amount
            self.save()
            return True
        return False

    def receive_gold(self, amount):
        """Add gold to shop reserves."""
        self.gold_reserves += amount
        self.save()


class ShopInventory(models.Model):
    """
    Represents items currently available in a shop's inventory.
    """

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='inventory'
    )

    item_template = models.ForeignKey(
        'ItemTemplate',
        on_delete=models.CASCADE,
        help_text="Template for the item being sold"
    )

    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Number of this item in stock"
    )

    base_price = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Base value of the item"
    )

    is_special = models.BooleanField(
        default=False,
        help_text="Special/rare item that doesn't restock automatically"
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['shop', 'item_template__name']
        unique_together = ['shop', 'item_template']

    def __str__(self):
        return f"{self.item_template.name} x{self.quantity} at {self.shop.name}"

    def get_sell_price(self):
        """Get the price this item sells for."""
        return self.shop.calculate_sell_price(self.base_price)

    def get_buy_price(self):
        """Get the price the shop will pay for this item."""
        return self.shop.calculate_buy_price(self.base_price)

    def remove_quantity(self, amount=1):
        """
        Remove quantity from stock.
        Returns True if successful, False if insufficient stock.
        """
        if self.quantity >= amount:
            self.quantity -= amount
            self.save()
            if self.quantity == 0 and not self.is_special:
                # Remove empty non-special items
                self.delete()
            return True
        return False

    def add_quantity(self, amount=1):
        """Add quantity to stock."""
        self.quantity += amount
        self.save()


class ShopTransaction(models.Model):
    """
    Logs all shop transactions for record keeping.
    """

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    customer = models.ForeignKey(
        ObjectDB,
        on_delete=models.SET_NULL,
        null=True,
        related_name='shop_transactions',
        help_text="Player or NPC who made the transaction"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('purchase', 'Purchase - Customer bought from shop'),
            ('sale', 'Sale - Customer sold to shop'),
        ]
    )

    item_name = models.CharField(
        max_length=200,
        help_text="Name of item involved in transaction"
    )

    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    price_per_item = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Price per individual item"
    )

    total_price = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total transaction price"
    )

    # Social combat influence
    social_discount = models.IntegerField(
        default=0,
        help_text="Percentage discount from social combat (0-100)"
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return (f"{self.get_transaction_type_display()}: {self.item_name} x{self.quantity} "
                f"for {self.total_price} crowns at {self.shop.name}")


class ShopRestockRule(models.Model):
    """
    Defines what items can appear in shops based on type, tier, and faction.

    This allows flexible configuration of shop inventory without hardcoding.
    """

    shop_type = models.CharField(
        max_length=50,
        choices=[
            ('weaponsmith', 'Weaponsmith'),
            ('armorsmith', 'Armorsmith'),
            ('jeweler', 'Jeweler'),
            ('alchemist', 'Alchemist'),
            ('general', 'General Store'),
            ('tailor', 'Tailor'),
            ('blacksmith', 'Blacksmith'),
            ('enchanter', 'Enchanter'),
        ],
        help_text="Which shop type this rule applies to"
    )

    min_tier = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="Minimum shop tier required"
    )

    max_tier = models.IntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="Maximum shop tier for this item"
    )

    item_template = models.ForeignKey(
        'ItemTemplate',
        on_delete=models.CASCADE,
        related_name='restock_rules',
        help_text="Item that can be stocked"
    )

    # Stocking parameters
    stock_chance = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage chance item appears during restock"
    )

    min_quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Minimum quantity when stocked"
    )

    max_quantity = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        help_text="Maximum quantity when stocked"
    )

    # Faction restrictions
    allowed_factions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of factions that can stock this (empty = all)"
    )

    restricted_factions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of factions that cannot stock this"
    )

    class Meta:
        ordering = ['shop_type', 'min_tier', 'item_template__name']

    def __str__(self):
        return f"{self.item_template.name} in {self.shop_type} (Tier {self.min_tier}-{self.max_tier})"

    def can_stock_in_shop(self, shop):
        """
        Check if this item can be stocked in the given shop.

        Args:
            shop: Shop instance

        Returns:
            bool: True if item can be stocked
        """
        # Check shop type
        if shop.shop_type != self.shop_type:
            return False

        # Check tier range
        if not (self.min_tier <= shop.tier <= self.max_tier):
            return False

        # Check faction restrictions
        if self.restricted_factions and shop.faction in self.restricted_factions:
            return False

        if self.allowed_factions and shop.faction not in self.allowed_factions:
            return False

        return True

    def roll_stock(self):
        """
        Roll to see if this item should be stocked.

        Returns:
            int: Quantity to stock (0 if roll fails)
        """
        if random.randint(1, 100) <= self.stock_chance:
            return random.randint(self.min_quantity, self.max_quantity)
        return 0
