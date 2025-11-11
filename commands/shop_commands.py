"""
Shop Commands for Witcher RPG

Commands for interacting with shops: browsing, buying, selling,
and starting social combat (haggling) with merchants.
"""

from evennia import Command
from world.witcher_rpg.shop_models import Shop, ShopInventory
from world.witcher_rpg.shop_system import ShopManager
from world.witcher_rpg.item_models import InventoryItem, Currency
from world.witcher_rpg.social_models import SocialEncounter
from world.witcher_rpg.social_combat import SocialEncounterManager


class CmdBrowse(Command):
    """
    Browse the inventory of a shop.

    Usage:
        browse
        browse <shop name>
        list
        shop

    Shows all items currently available for purchase in the shop,
    along with prices, quantities, and tiers.
    """

    key = "browse"
    aliases = ["list", "shop", "wares"]
    locks = "cmd:all()"
    help_category = "Commerce"

    def func(self):
        caller = self.caller
        location = caller.location

        # Find shop in current location
        shop = ShopManager.get_shop_at_location(location)

        if not shop:
            caller.msg("There is no shop here.")
            return

        # Display inventory
        inventory_display = ShopManager.format_shop_inventory(shop, caller)
        caller.msg(inventory_display)


class CmdBuy(Command):
    """
    Purchase items from a shop.

    Usage:
        buy <item> [quantity]
        buy sword
        buy potion 3

    Purchases the specified item from the shop. If you have recently
    won social combat against the merchant, you may have a discount.

    The item will be added to your inventory and gold will be deducted.
    """

    key = "buy"
    aliases = ["purchase"]
    locks = "cmd:all()"
    help_category = "Commerce"

    def func(self):
        caller = self.caller
        location = caller.location

        if not self.args:
            caller.msg("Usage: buy <item> [quantity]")
            return

        # Find shop
        shop = ShopManager.get_shop_at_location(location)
        if not shop:
            caller.msg("There is no shop here.")
            return

        # Parse arguments
        args_list = self.args.strip().split()
        item_name = args_list[0]
        quantity = 1

        if len(args_list) > 1:
            try:
                quantity = int(args_list[1])
                if quantity < 1:
                    caller.msg("Quantity must be at least 1.")
                    return
            except ValueError:
                caller.msg("Invalid quantity. Must be a number.")
                return

        # Find item in shop
        inventory_items = shop.inventory.filter(
            item_template__name__icontains=item_name,
            quantity__gt=0
        )

        if not inventory_items.exists():
            caller.msg(f"'{item_name}' is not available in this shop.")
            return

        if inventory_items.count() > 1:
            caller.msg(f"Multiple items match '{item_name}'. Please be more specific:")
            for item in inventory_items:
                caller.msg(f"  - {item.item_template.name}")
            return

        inventory_item = inventory_items.first()

        # Check for social combat discount
        # In practice, you'd store this temporarily or in a session variable
        social_discount = caller.ndb.shop_discount or 0

        # Attempt purchase
        result = ShopManager.purchase_item(
            shop=shop,
            customer=caller,
            item_template=inventory_item.item_template,
            quantity=quantity,
            social_discount=social_discount
        )

        if result['success']:
            if result['discount'] > 0:
                caller.msg(
                    f"You purchase {result['quantity']}x {result['item']} "
                    f"for {result['total_cost']} crowns "
                    f"(|g{result['discount']}% discount!|n)"
                )
            else:
                caller.msg(
                    f"You purchase {result['quantity']}x {result['item']} "
                    f"for {result['total_cost']} crowns."
                )

            caller.msg(f"Remaining gold: {result['remaining_gold']} crowns")

            # Clear discount after use
            caller.ndb.shop_discount = 0
        else:
            caller.msg(f"|rPurchase failed:|n {result['message']}")


class CmdSell(Command):
    """
    Sell items from your inventory to a shop.

    Usage:
        sell <item> [quantity]
        sell sword
        sell potion 2

    Sells the specified item to the shop. The shop will only buy items
    relevant to its type (e.g., weaponsmiths buy weapons).

    Item condition affects the price - damaged items sell for less.
    If you recently won social combat, you may get a better price.
    """

    key = "sell"
    locks = "cmd:all()"
    help_category = "Commerce"

    def func(self):
        caller = self.caller
        location = caller.location

        if not self.args:
            caller.msg("Usage: sell <item> [quantity]")
            return

        # Find shop
        shop = ShopManager.get_shop_at_location(location)
        if not shop:
            caller.msg("There is no shop here.")
            return

        # Parse arguments
        args_list = self.args.strip().split()
        item_name = args_list[0]
        quantity = 1

        if len(args_list) > 1:
            try:
                quantity = int(args_list[1])
                if quantity < 1:
                    caller.msg("Quantity must be at least 1.")
                    return
            except ValueError:
                caller.msg("Invalid quantity. Must be a number.")
                return

        # Find item in player's inventory
        inventory_items = InventoryItem.objects.filter(
            character=caller,
            template__name__icontains=item_name
        )

        if not inventory_items.exists():
            caller.msg(f"You don't have any '{item_name}' to sell.")
            return

        if inventory_items.count() > 1:
            caller.msg(f"Multiple items match '{item_name}'. Please be more specific:")
            for item in inventory_items:
                condition_text = f"({item.condition}% condition)"
                caller.msg(f"  - {item.template.name} {condition_text}")
            return

        inventory_item = inventory_items.first()

        # Check for social combat bonus
        social_bonus = caller.ndb.shop_bonus or 0

        # Attempt sale
        result = ShopManager.sell_item(
            shop=shop,
            customer=caller,
            inventory_item=inventory_item,
            quantity=quantity,
            social_bonus=social_bonus
        )

        if result['success']:
            if result['bonus'] > 0:
                caller.msg(
                    f"You sell {result['quantity']}x {result['item']} "
                    f"for {result['total_payment']} crowns "
                    f"(|g{result['bonus']}% bonus!|n)"
                )
            else:
                caller.msg(
                    f"You sell {result['quantity']}x {result['item']} "
                    f"for {result['total_payment']} crowns."
                )

            caller.msg(f"New gold total: {result['new_gold']} crowns")

            # Clear bonus after use
            caller.ndb.shop_bonus = 0
        else:
            caller.msg(f"|rSale failed:|n {result['message']}")


class CmdHaggle(Command):
    """
    Haggle with the merchant to get better prices.

    Usage:
        haggle
        negotiate

    Starts a social combat encounter (negotiation type) with the shop's
    merchant. If you win, you'll receive a discount on purchases or
    bonus payment on sales for your next transaction.

    This uses the Intrigue system - charm, cunning, appearance, and graces
    determine success. Higher social rank makes it easier.

    Victory margin determines discount/bonus:
        Small victory (1-20 capital): 5-15% discount
        Medium victory (21-40): 15-30% discount
        Large victory (41+): 30-50% discount
    """

    key = "haggle"
    aliases = ["negotiate", "bargain"]
    locks = "cmd:all()"
    help_category = "Commerce"

    def func(self):
        caller = self.caller
        location = caller.location

        # Find shop
        shop = ShopManager.get_shop_at_location(location)
        if not shop:
            caller.msg("There is no shop here.")
            return

        if not shop.merchant:
            caller.msg("There is no merchant here to haggle with.")
            return

        # Check if already in social combat
        existing_encounter = SocialEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if existing_encounter:
            caller.msg("There is already an active negotiation here!")
            return

        # Create negotiation encounter
        encounter = SocialEncounterManager.create_encounter(
            location=location,
            encounter_type='negotiation',
            name=f"Haggling at {shop.name}",
            stakes={'description': 'Better prices on next transaction'}
        )

        # Add participants
        caller_participant = SocialEncounterManager.add_participant(
            encounter, caller, wealth_level=2
        )

        # Determine merchant wealth level based on shop tier
        merchant_wealth_map = {1: 3, 2: 4, 3: 5, 4: 6}
        merchant_wealth = merchant_wealth_map.get(shop.tier, 4)

        merchant_participant = SocialEncounterManager.add_participant(
            encounter, shop.merchant, wealth_level=merchant_wealth
        )

        # Announce start
        location.msg_contents(
            f"|y{'=' * 70}|n\n"
            f"|c{caller.name}|n begins |yhaggling|n with |c{shop.merchant.name}|n!\n"
            f"|y{'=' * 70}|n"
        )

        # Show initiative order
        participants = encounter.participants.all().order_by('initiative_order')
        location.msg_contents("\n|wInitiative Order:|n")
        for p in participants:
            capital_bar = self._make_capital_bar(p.current_social_capital, p.max_social_capital)
            location.msg_contents(
                f"  {p.initiative_order + 1}. |c{p.character.name}|n "
                f"- Social Capital: {capital_bar}"
            )

        # Show whose turn it is
        current = encounter.get_current_participant()
        if current:
            location.msg_contents(
                f"\n|yIt is |c{current.character.name}|y's turn.|n\n"
                f"Win to get a discount on your next purchase or bonus on your next sale!"
            )

    def _make_capital_bar(self, current, maximum):
        """Create a visual bar showing social capital."""
        if maximum == 0:
            return "|r[----------]|n 0/0"

        percent = current / maximum
        bar_length = 10
        filled = int(percent * bar_length)
        empty = bar_length - filled

        if percent > 0.6:
            color = '|g'
        elif percent > 0.3:
            color = '|y'
        else:
            color = '|r'

        bar = f"{color}[{'█' * filled}{'░' * empty}]|n {current}/{maximum}"
        return bar


class CmdShopManage(Command):
    """
    Manage your owned shop (owner only).

    Usage:
        shopmanage
        shopmanage restock
        shopmanage prices <markup> <buyback>
        shopmanage open
        shopmanage close

    Owner commands:
        restock - Force immediate restock
        prices - Adjust markup and buyback percentages
        open/close - Open or close the shop
        (no args) - View shop status and recent transactions

    Examples:
        shopmanage restock
        shopmanage prices 140 60
        shopmanage open
    """

    key = "shopmanage"
    aliases = ["manageshop"]
    locks = "cmd:all()"
    help_category = "Commerce"

    def func(self):
        caller = self.caller
        location = caller.location

        # Find shop
        shop = ShopManager.get_shop_at_location(location)
        if not shop:
            # Check if caller owns any shops in this location
            owned_shops = Shop.objects.filter(location=location, owner=caller)
            if owned_shops.exists():
                shop = owned_shops.first()
            else:
                caller.msg("There is no shop here, or you don't own it.")
                return

        # Check ownership
        if shop.owner != caller:
            caller.msg("You don't own this shop.")
            return

        if not self.args:
            # Display shop status
            self._display_shop_status(shop)
            return

        args_list = self.args.strip().split()
        command = args_list[0].lower()

        if command == "restock":
            self._handle_restock(shop)
        elif command == "prices":
            if len(args_list) < 3:
                caller.msg("Usage: shopmanage prices <markup%> <buyback%>")
                return
            self._handle_prices(shop, args_list[1], args_list[2])
        elif command == "open":
            self._handle_open(shop)
        elif command == "close":
            self._handle_close(shop)
        else:
            caller.msg("Unknown command. Use: restock, prices, open, or close")

    def _display_shop_status(self, shop):
        """Display detailed shop status."""
        from world.witcher_rpg.shop_models import ShopTransaction

        lines = []
        lines.append(f"|y{'=' * 70}|n")
        lines.append(f"|wShop Management: {shop.name}|n")
        lines.append(f"|y{'=' * 70}|n")
        lines.append(f"Type: {shop.get_shop_type_display()}")
        lines.append(f"Tier: {shop.tier}")
        lines.append(f"Faction: {shop.get_faction_display()}")
        lines.append(f"Status: {'|gOpen|n' if shop.is_open else '|rClosed|n'}")
        lines.append("")
        lines.append(f"|wFinancials:|n")
        lines.append(f"Gold Reserves: {shop.gold_reserves} crowns")
        lines.append(f"Markup: {shop.markup_percentage}% (sell price)")
        lines.append(f"Buyback: {shop.buyback_percentage}% (buy price)")
        lines.append("")
        lines.append(f"|wInventory:|n")
        inventory_count = shop.inventory.count()
        total_items = sum(item.quantity for item in shop.inventory.all())
        lines.append(f"Unique items: {inventory_count}")
        lines.append(f"Total items: {total_items}")
        lines.append("")
        lines.append(f"|wRecent Transactions:|n")

        recent = ShopTransaction.objects.filter(shop=shop)[:5]
        if recent.exists():
            for trans in recent:
                trans_type = "📥" if trans.transaction_type == 'sale' else "📤"
                lines.append(
                    f"{trans_type} {trans.item_name} x{trans.quantity} "
                    f"for {trans.total_price} crowns"
                )
        else:
            lines.append("No recent transactions")

        lines.append("")
        lines.append("|yCommands:|n shopmanage restock | prices | open | close")

        self.caller.msg("\n".join(lines))

    def _handle_restock(self, shop):
        """Force shop restock."""
        result = ShopManager.restock_shop(shop, force=True)

        if result['success']:
            self.caller.msg(
                f"|gRestocked {shop.name}!|n\n"
                f"Added {result['total_quantity']} items across "
                f"{len(result['items_added'])} different types."
            )
        else:
            self.caller.msg(f"|rRestock failed:|n {result.get('message', 'Unknown error')}")

    def _handle_prices(self, shop, markup_str, buyback_str):
        """Adjust shop prices."""
        try:
            markup = int(markup_str)
            buyback = int(buyback_str)

            if not (100 <= markup <= 500):
                self.caller.msg("Markup must be between 100% and 500%.")
                return

            if not (10 <= buyback <= 100):
                self.caller.msg("Buyback must be between 10% and 100%.")
                return

            shop.markup_percentage = markup
            shop.buyback_percentage = buyback
            shop.save()

            self.caller.msg(
                f"Updated prices for {shop.name}:\n"
                f"Markup: {markup}% | Buyback: {buyback}%"
            )

        except ValueError:
            self.caller.msg("Prices must be numbers.")

    def _handle_open(self, shop):
        """Open the shop."""
        if shop.is_open:
            self.caller.msg(f"{shop.name} is already open.")
            return

        shop.is_open = True
        shop.save()
        self.caller.msg(f"|g{shop.name} is now open for business!|n")

    def _handle_close(self, shop):
        """Close the shop."""
        if not shop.is_open:
            self.caller.msg(f"{shop.name} is already closed.")
            return

        shop.is_open = False
        shop.save()
        self.caller.msg(f"|y{shop.name} is now closed.|n")
