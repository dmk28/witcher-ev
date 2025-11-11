"""
Shop Management System for Witcher RPG

Handles shop restocking, transactions, and social combat integration.
"""

from datetime import datetime, timedelta
from django.utils import timezone
from world.witcher_rpg.shop_models import Shop, ShopInventory, ShopTransaction, ShopRestockRule
from world.witcher_rpg.item_models import ItemTemplate, Currency
import random


class ShopManager:
    """
    Manages shop operations including restocking, buying, and selling.
    """

    @staticmethod
    def restock_shop(shop, force=False):
        """
        Restock a shop based on its type, tier, and faction.

        Args:
            shop: Shop instance to restock
            force: If True, restock regardless of time interval

        Returns:
            dict: Summary of restocking results
        """
        # Check if it's time to restock
        if not force:
            time_since_restock = timezone.now() - shop.last_restock
            if time_since_restock < timedelta(hours=shop.restock_interval_hours):
                return {
                    'success': False,
                    'message': 'Not yet time to restock',
                    'next_restock': shop.last_restock + timedelta(hours=shop.restock_interval_hours)
                }

        # Clear non-special items
        shop.inventory.filter(is_special=False).delete()

        # Get applicable restock rules
        rules = ShopRestockRule.objects.filter(
            shop_type=shop.shop_type,
            min_tier__lte=shop.tier,
            max_tier__gte=shop.tier
        )

        # Filter by faction
        applicable_rules = [rule for rule in rules if rule.can_stock_in_shop(shop)]

        # Stock items based on rules
        items_added = []
        total_quantity = 0

        for rule in applicable_rules:
            quantity = rule.roll_stock()
            if quantity > 0:
                # Create or update inventory entry
                inventory_item, created = ShopInventory.objects.get_or_create(
                    shop=shop,
                    item_template=rule.item_template,
                    defaults={
                        'quantity': quantity,
                        'base_price': rule.item_template.base_value,
                        'is_special': False
                    }
                )

                if not created:
                    inventory_item.quantity += quantity
                    inventory_item.save()

                items_added.append({
                    'name': rule.item_template.name,
                    'quantity': quantity,
                    'price': inventory_item.get_sell_price()
                })
                total_quantity += quantity

        # Update last restock time
        shop.last_restock = timezone.now()
        shop.save()

        return {
            'success': True,
            'items_added': items_added,
            'total_quantity': total_quantity,
            'shop': shop
        }

    @staticmethod
    def purchase_item(shop, customer, item_template, quantity=1, social_discount=0):
        """
        Customer purchases items from shop.

        Args:
            shop: Shop instance
            customer: Character purchasing
            item_template: ItemTemplate being purchased
            quantity: Number to purchase
            social_discount: Percentage discount from social combat (0-100)

        Returns:
            dict: Transaction result
        """
        # Find inventory item
        try:
            inventory_item = shop.inventory.get(item_template=item_template)
        except ShopInventory.DoesNotExist:
            return {
                'success': False,
                'message': f"{item_template.name} is not in stock."
            }

        # Check stock
        if inventory_item.quantity < quantity:
            return {
                'success': False,
                'message': f"Only {inventory_item.quantity} available."
            }

        # Calculate price
        base_price = inventory_item.get_sell_price()

        # Apply social discount
        if social_discount > 0:
            discount_amount = int(base_price * (social_discount / 100))
            final_price = max(1, base_price - discount_amount)
        else:
            final_price = base_price

        total_cost = final_price * quantity

        # Check customer's gold
        customer_gold = Currency.objects.filter(character=customer).first()
        if not customer_gold or customer_gold.crowns < total_cost:
            return {
                'success': False,
                'message': f"Insufficient funds. Need {total_cost} crowns."
            }

        # Process transaction
        # Deduct customer gold
        customer_gold.crowns -= total_cost
        customer_gold.save()

        # Add to shop reserves
        shop.receive_gold(total_cost)

        # Remove from inventory
        inventory_item.remove_quantity(quantity)

        # Create items for customer
        from world.witcher_rpg.item_models import InventoryItem

        for _ in range(quantity):
            InventoryItem.objects.create(
                character=customer,
                template=item_template,
                condition=100,
                is_equipped=False
            )

        # Log transaction
        ShopTransaction.objects.create(
            shop=shop,
            customer=customer,
            transaction_type='purchase',
            item_name=item_template.name,
            quantity=quantity,
            price_per_item=final_price,
            total_price=total_cost,
            social_discount=social_discount
        )

        return {
            'success': True,
            'item': item_template.name,
            'quantity': quantity,
            'price_per': final_price,
            'total_cost': total_cost,
            'discount': social_discount,
            'remaining_gold': customer_gold.crowns
        }

    @staticmethod
    def sell_item(shop, customer, inventory_item, quantity=1, social_bonus=0):
        """
        Customer sells items to shop.

        Args:
            shop: Shop instance
            customer: Character selling
            inventory_item: InventoryItem being sold
            quantity: Number to sell
            social_bonus: Percentage bonus price from social combat (0-100)

        Returns:
            dict: Transaction result
        """
        # Check if shop accepts this item type
        if not ShopManager._shop_accepts_item(shop, inventory_item.template):
            return {
                'success': False,
                'message': f"{shop.name} doesn't buy {inventory_item.template.name}."
            }

        # Calculate price
        base_buyback = shop.calculate_buy_price(inventory_item.template.base_value)

        # Apply condition modifier
        condition_modifier = inventory_item.condition / 100.0
        adjusted_price = int(base_buyback * condition_modifier)

        # Apply social bonus
        if social_bonus > 0:
            bonus_amount = int(adjusted_price * (social_bonus / 100))
            final_price = adjusted_price + bonus_amount
        else:
            final_price = adjusted_price

        total_payment = final_price * quantity

        # Check shop's gold
        if not shop.can_afford(total_payment):
            return {
                'success': False,
                'message': f"{shop.name} doesn't have enough gold."
            }

        # Process transaction
        # Deduct shop gold
        shop.pay_gold(total_payment)

        # Add to customer gold
        customer_gold, created = Currency.objects.get_or_create(
            character=customer,
            defaults={'crowns': 0, 'orens': 0, 'florens': 0}
        )
        customer_gold.crowns += total_payment
        customer_gold.save()

        # Remove from customer inventory
        # (In a real implementation, you'd handle multiple items properly)
        inventory_item.delete()

        # Add to shop inventory (if shop will resell)
        if shop.buyback_percentage >= 40:  # Shop resells items bought at good prices
            shop_inventory, created = ShopInventory.objects.get_or_create(
                shop=shop,
                item_template=inventory_item.template,
                defaults={
                    'quantity': quantity,
                    'base_price': inventory_item.template.base_value,
                    'is_special': True  # Player-sold items are special
                }
            )
            if not created:
                shop_inventory.add_quantity(quantity)

        # Log transaction
        ShopTransaction.objects.create(
            shop=shop,
            customer=customer,
            transaction_type='sale',
            item_name=inventory_item.template.name,
            quantity=quantity,
            price_per_item=final_price,
            total_price=total_payment,
            social_discount=social_bonus  # Using discount field for bonus
        )

        return {
            'success': True,
            'item': inventory_item.template.name,
            'quantity': quantity,
            'price_per': final_price,
            'total_payment': total_payment,
            'bonus': social_bonus,
            'new_gold': customer_gold.crowns
        }

    @staticmethod
    def _shop_accepts_item(shop, item_template):
        """
        Check if a shop accepts a particular item type.

        Args:
            shop: Shop instance
            item_template: ItemTemplate to check

        Returns:
            bool: True if shop accepts this item type
        """
        shop_item_types = {
            'weaponsmith': ['weapon'],
            'armorsmith': ['armor'],
            'jeweler': ['jewelry', 'gem', 'luxury'],
            'alchemist': ['potion', 'ingredient', 'oil'],
            'general': ['consumable', 'material', 'tool'],
            'tailor': ['clothing', 'luxury'],
            'blacksmith': ['weapon', 'armor', 'tool', 'material'],
            'enchanter': ['scroll', 'rune', 'magic_item'],
        }

        accepted_types = shop_item_types.get(shop.shop_type, [])
        return item_template.item_type in accepted_types or shop.shop_type == 'general'

    @staticmethod
    def get_shop_at_location(location):
        """
        Get the shop at a given location.

        Args:
            location: Room object

        Returns:
            Shop or None
        """
        try:
            return Shop.objects.get(location=location, is_open=True)
        except Shop.DoesNotExist:
            return None
        except Shop.MultipleObjectsReturned:
            # Return first open shop if multiple
            return Shop.objects.filter(location=location, is_open=True).first()

    @staticmethod
    def apply_social_combat_discount(shop, customer, victory_margin):
        """
        Calculate discount percentage based on social combat victory.

        This is called after a customer defeats the merchant in social combat.

        Args:
            shop: Shop instance
            customer: Character who won social combat
            victory_margin: Remaining social capital after victory

        Returns:
            dict: Discount/bonus information
        """
        # Base discount scales with victory margin
        # Small victory (1-20): 5-15% discount
        # Medium victory (21-40): 15-30% discount
        # Large victory (41+): 30-50% discount

        if victory_margin <= 20:
            discount = 5 + (victory_margin // 2)
        elif victory_margin <= 40:
            discount = 15 + ((victory_margin - 20) // 2)
        else:
            discount = 30 + min((victory_margin - 40) // 3, 20)

        discount = min(discount, 50)  # Cap at 50% discount

        # Store discount in a temporary attribute
        # In practice, you'd want to store this in a more permanent way
        # or apply it immediately to the next transaction

        return {
            'discount_percentage': discount,
            'valid_for': 'next_transaction',
            'message': (f"You've successfully negotiated a {discount}% discount "
                       f"at {shop.name}!")
        }

    @staticmethod
    def format_shop_inventory(shop, customer=None):
        """
        Format shop inventory for display.

        Args:
            shop: Shop instance
            customer: Optional customer for personalized info

        Returns:
            str: Formatted inventory listing
        """
        lines = []
        lines.append(f"|y{'=' * 70}|n")
        lines.append(f"|w{shop.name}|n - {shop.get_shop_type_display()}")
        lines.append(f"Tier {shop.tier} | {shop.get_faction_display()}")

        if shop.merchant:
            lines.append(f"Merchant: |c{shop.merchant.name}|n")

        lines.append(f"|y{'=' * 70}|n")

        # Get inventory
        inventory = shop.inventory.filter(quantity__gt=0).order_by('item_template__tier', 'item_template__name')

        if not inventory.exists():
            lines.append("|rShop is currently out of stock.|n")
            return "\n".join(lines)

        lines.append(f"\n{'Item':<30} {'Qty':<5} {'Price':<10} {'Tier'}")
        lines.append("-" * 70)

        for item in inventory:
            price = item.get_sell_price()
            tier_display = "★" * item.item_template.tier
            special_marker = " |y*|n" if item.is_special else ""

            lines.append(
                f"{item.item_template.name:<30} "
                f"{item.quantity:<5} "
                f"{price:<10} "
                f"{tier_display}{special_marker}"
            )

        lines.append("-" * 70)
        lines.append("|yCommands:|n buy <item>, sell <item>, haggle (start social combat for discount)")

        return "\n".join(lines)


class ShopCreator:
    """
    Helper class for creating and configuring shops.
    """

    @staticmethod
    def create_shop(location, name, shop_type, tier=1, faction='independent',
                   owner=None, merchant=None):
        """
        Create a new shop.

        Args:
            location: Room where shop is located
            name: Shop name
            shop_type: Type of shop
            tier: Investment tier (1-4)
            faction: Faction affiliation
            owner: Optional owner
            merchant: Optional merchant NPC

        Returns:
            Shop: Created shop instance
        """
        # Calculate starting gold based on tier
        gold_by_tier = {
            1: 500,
            2: 2000,
            3: 10000,
            4: 50000,
        }

        shop = Shop.objects.create(
            name=name,
            location=location,
            owner=owner,
            merchant=merchant,
            shop_type=shop_type,
            tier=tier,
            faction=faction,
            gold_reserves=gold_by_tier.get(tier, 1000),
            markup_percentage=150,
            buyback_percentage=50,
            restock_interval_hours=24,
            is_open=True
        )

        # Initial restock
        ShopManager.restock_shop(shop, force=True)

        return shop

    @staticmethod
    def create_basic_restock_rules():
        """
        Create basic restock rules for common items.

        This would typically be run once during initial setup.
        Returns a list of created rules.
        """
        # This is a template - you'd populate this with actual ItemTemplate references
        # after creating your item templates

        rules = []

        # Example structure (you'll need actual ItemTemplate objects)
        # Weaponsmith rules
        weaponsmith_items = [
            # ('template_name', min_tier, max_tier, stock_chance, min_qty, max_qty)
            ('iron_sword', 1, 2, 80, 2, 5),
            ('steel_sword', 2, 3, 60, 1, 3),
            ('silver_sword', 3, 4, 40, 1, 2),
            ('crossbow', 2, 4, 50, 1, 3),
        ]

        # Alchemist rules
        alchemist_items = [
            ('swallow_potion', 1, 4, 70, 3, 8),
            ('cat_potion', 2, 4, 50, 2, 5),
            ('thunderbolt_potion', 3, 4, 40, 1, 3),
        ]

        return rules
