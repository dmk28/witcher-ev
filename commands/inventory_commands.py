"""
Inventory and item management commands for Witcher RPG.
Handles equipment, item usage, trading, and bank operations.
"""

from evennia import Command
from evennia.utils.evtable import EvTable
from world.witcher_rpg.item_models import InventoryItem, ItemTemplate, BankStorage, Currency
from world.witcher_rpg.loot_system import CraftingSystem


class CmdInventory(Command):
    """
    View your inventory and equipment.

    Usage:
      inventory
      inv

    Shows all items in your inventory, equipped items, total weight,
    and current gold.
    """

    key = "inventory"
    aliases = ["inv"]
    locks = "cmd:all()"
    help_category = "Inventory"

    def func(self):
        caller = self.caller

        if not hasattr(caller, 'db_character') or not caller.db_character:
            self.caller.msg("You don't have a character sheet.")
            return

        character = caller.db_character

        # Get currency
        try:
            currency = Currency.objects.get(character=caller)
            gold = currency.gold
        except Currency.DoesNotExist:
            gold = 0

        # Get inventory items
        inventory_items = InventoryItem.objects.filter(owner=caller).order_by(
            '-is_equipped', '-template__tier', 'template__name'
        )

        if not inventory_items.exists():
            self.caller.msg("|yYou have no items in your inventory.|n")
            self.caller.msg(f"|yGold:|n {gold}")
            return

        # Build output
        output = []
        output.append("|w" + "=" * 70 + "|n")
        output.append("|w" + f"{'Inventory for ' + character.character_name:^70}" + "|n")
        output.append("|w" + "=" * 70 + "|n")
        output.append(f"|yGold:|n {gold}")
        output.append("")

        # Equipped items
        equipped = [item for item in inventory_items if item.is_equipped]
        if equipped:
            output.append("|g=== Equipped Items ===|n")
            for item in equipped:
                name = item.custom_name if item.custom_name else item.template.name
                tier = item.template.get_tier_display()
                condition = item.condition

                # Color code by condition
                if condition >= 80:
                    cond_color = "|g"
                elif condition >= 50:
                    cond_color = "|y"
                else:
                    cond_color = "|r"

                # Show bonuses
                bonuses_str = ""
                if item.template.damage_bonus > 0:
                    bonuses_str += f" |c[+{item.template.damage_bonus} Dmg]|n"
                if item.template.armor_value > 0:
                    bonuses_str += f" |c[{item.template.armor_value} Armor]|n"

                stat_bonuses = item.get_stat_bonuses()
                if stat_bonuses:
                    bonus_list = [f"+{v} {k}" for k, v in stat_bonuses.items()]
                    bonuses_str += f" |c[{', '.join(bonus_list)}]|n"

                output.append(f"  |w{name}|n ({tier}){bonuses_str} {cond_color}[{condition}%]|n")
            output.append("")

        # Unequipped items
        unequipped = [item for item in inventory_items if not item.is_equipped]
        if unequipped:
            output.append("|y=== Inventory ===|n")
            total_weight = 0

            for item in unequipped:
                name = item.custom_name if item.custom_name else item.template.name
                tier = item.template.get_tier_display()
                weight = item.get_total_weight()
                total_weight += weight

                # Show quantity for stackable
                qty_str = ""
                if item.template.is_stackable and item.quantity > 1:
                    qty_str = f" |yx{item.quantity}|n"

                # Category icon
                category_icons = {
                    'weapon': '⚔',
                    'armor': '🛡',
                    'consumable': '🧪',
                    'material': '📦',
                    'quest': '📜',
                    'misc': '📌'
                }
                icon = category_icons.get(item.template.category, '📌')

                output.append(f"  {icon} |w{name}|n ({tier}){qty_str} |c[{weight:.1f} lbs]|n")

            output.append(f"\n|yTotal Weight:|n {total_weight:.1f} lbs")

        output.append("|w" + "=" * 70 + "|n")
        self.caller.msg("\n".join(output))


class CmdEquip(Command):
    """
    Equip or unequip an item.

    Usage:
      equip <item name>
      unequip <item name>

    Equips an item from your inventory or unequips an equipped item.
    """

    key = "equip"
    aliases = []
    locks = "cmd:all()"
    help_category = "Inventory"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: equip <item name>")
            return

        item_name = self.args.strip()

        # Find item in inventory
        items = InventoryItem.objects.filter(
            owner=self.caller,
            is_equipped=False
        )

        # Try exact match first
        item = None
        for inv_item in items:
            check_name = inv_item.custom_name if inv_item.custom_name else inv_item.template.name
            if check_name.lower() == item_name.lower():
                item = inv_item
                break

        # Try partial match
        if not item:
            for inv_item in items:
                check_name = inv_item.custom_name if inv_item.custom_name else inv_item.template.name
                if item_name.lower() in check_name.lower():
                    item = inv_item
                    break

        if not item:
            self.caller.msg(f"You don't have an unequipped item named '{item_name}'.")
            return

        # Check if it's equippable
        if item.template.category not in ['weapon', 'armor']:
            self.caller.msg(f"You cannot equip {item.template.name}.")
            return

        # Equip it
        item.is_equipped = True
        item.save()

        name = item.custom_name if item.custom_name else item.template.name
        self.caller.msg(f"|gYou equip {name}.|n")
        self.caller.location.msg_contents(
            f"{self.caller.name} equips {name}.",
            exclude=self.caller
        )


class CmdUnequip(Command):
    """
    Unequip an equipped item.

    Usage:
      unequip <item name>

    Unequips an item and returns it to your inventory.
    """

    key = "unequip"
    aliases = []
    locks = "cmd:all()"
    help_category = "Inventory"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: unequip <item name>")
            return

        item_name = self.args.strip()

        # Find equipped item
        items = InventoryItem.objects.filter(
            owner=self.caller,
            is_equipped=True
        )

        # Try exact match first
        item = None
        for inv_item in items:
            check_name = inv_item.custom_name if inv_item.custom_name else inv_item.template.name
            if check_name.lower() == item_name.lower():
                item = inv_item
                break

        # Try partial match
        if not item:
            for inv_item in items:
                check_name = inv_item.custom_name if inv_item.custom_name else inv_item.template.name
                if item_name.lower() in check_name.lower():
                    item = inv_item
                    break

        if not item:
            self.caller.msg(f"You don't have an equipped item named '{item_name}'.")
            return

        # Unequip it
        item.is_equipped = False
        item.save()

        name = item.custom_name if item.custom_name else item.template.name
        self.caller.msg(f"|yYou unequip {name}.|n")
        self.caller.location.msg_contents(
            f"{self.caller.name} unequips {name}.",
            exclude=self.caller
        )


class CmdUse(Command):
    """
    Use a consumable item.

    Usage:
      use <item name>

    Uses a consumable item from your inventory. The item will be consumed
    and its effects applied.
    """

    key = "use"
    aliases = []
    locks = "cmd:all()"
    help_category = "Inventory"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: use <item name>")
            return

        item_name = self.args.strip()

        # Find consumable item
        items = InventoryItem.objects.filter(
            owner=self.caller,
            template__category='consumable'
        )

        # Try exact match first
        item = None
        for inv_item in items:
            check_name = inv_item.custom_name if inv_item.custom_name else inv_item.template.name
            if check_name.lower() == item_name.lower():
                item = inv_item
                break

        # Try partial match
        if not item:
            for inv_item in items:
                check_name = inv_item.custom_name if inv_item.custom_name else inv_item.template.name
                if item_name.lower() in check_name.lower():
                    item = inv_item
                    break

        if not item:
            self.caller.msg(f"You don't have a consumable item named '{item_name}'.")
            return

        # Use the item
        name = item.custom_name if item.custom_name else item.template.name

        # TODO: Apply item effects based on special_ability or stat_bonuses
        # For now, just show a message
        self.caller.msg(f"|gYou use {name}.|n")
        self.caller.location.msg_contents(
            f"{self.caller.name} uses {name}.",
            exclude=self.caller
        )

        # Reduce quantity or delete
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()


class CmdGive(Command):
    """
    Give an item to another character.

    Usage:
      give <item name> to <character>

    Transfers an item from your inventory to another character's inventory.
    """

    key = "give"
    aliases = []
    locks = "cmd:all()"
    help_category = "Inventory"

    def func(self):
        if not self.args or ' to ' not in self.args:
            self.caller.msg("Usage: give <item name> to <character>")
            return

        parts = self.args.split(' to ', 1)
        item_name = parts[0].strip()
        target_name = parts[1].strip()

        # Find target
        target = self.caller.search(target_name)
        if not target:
            return

        if target == self.caller:
            self.caller.msg("You cannot give items to yourself.")
            return

        # Find item in inventory (unequipped only)
        items = InventoryItem.objects.filter(
            owner=self.caller,
            is_equipped=False
        )

        # Try exact match first
        item = None
        for inv_item in items:
            check_name = inv_item.custom_name if inv_item.custom_name else inv_item.template.name
            if check_name.lower() == item_name.lower():
                item = inv_item
                break

        # Try partial match
        if not item:
            for inv_item in items:
                check_name = inv_item.custom_name if inv_item.custom_name else inv_item.template.name
                if item_name.lower() in check_name.lower():
                    item = inv_item
                    break

        if not item:
            self.caller.msg(f"You don't have an unequipped item named '{item_name}'.")
            return

        # Transfer item
        name = item.custom_name if item.custom_name else item.template.name

        # Change ownership
        item.owner = target
        item.save()

        self.caller.msg(f"|yYou give {name} to {target.name}.|n")
        target.msg(f"|g{self.caller.name} gives you {name}.|n")
        self.caller.location.msg_contents(
            f"{self.caller.name} gives {name} to {target.name}.",
            exclude=[self.caller, target]
        )


class CmdBank(Command):
    """
    Manage your bank storage.

    Usage:
      bank                           - View bank contents
      bank/deposit <amount> gold     - Deposit gold
      bank/withdraw <amount> gold    - Withdraw gold
      bank/deposit <item name>       - Deposit item
      bank/withdraw <item name>      - Withdraw item

    Bank storage is safe and accessible from any bank room.
    """

    key = "bank"
    aliases = []
    locks = "cmd:all()"
    help_category = "Inventory"

    def func(self):
        caller = self.caller

        # Check if in a bank room
        if not caller.location:
            caller.msg("You need to be in a location to use the bank.")
            return

        # Check if location is a bank
        from world.witcher_rpg.room_models import WitcherRoom
        try:
            witcher_room = WitcherRoom.objects.get(room_object=caller.location)
            if witcher_room.room_type != 'bank':
                caller.msg("|rYou must be in a bank to access your storage.|n")
                return
        except WitcherRoom.DoesNotExist:
            caller.msg("|rThis room does not have bank facilities.|n")
            return

        # Get or create bank storage
        bank, created = BankStorage.objects.get_or_create(
            owner=caller,
            defaults={'gold_stored': 0, 'max_storage_slots': 100}
        )

        # Get currency
        currency, _ = Currency.objects.get_or_create(
            character=caller,
            defaults={'gold': 0}
        )

        # View bank
        if not self.switches:
            self._view_bank(bank)
            return

        # Deposit
        if 'deposit' in self.switches:
            self._deposit(bank, currency)
            return

        # Withdraw
        if 'withdraw' in self.switches:
            self._withdraw(bank, currency)
            return

        caller.msg("Invalid bank command. See 'help bank'.")

    def _view_bank(self, bank):
        """Display bank contents."""
        output = []
        output.append("|w" + "=" * 70 + "|n")
        output.append("|w" + f"{'Bank Storage':^70}" + "|n")
        output.append("|w" + "=" * 70 + "|n")
        output.append(f"|yGold Stored:|n {bank.gold_stored}")
        output.append(f"|yStorage Slots:|n {bank.get_item_count()}/{bank.max_storage_slots}")
        output.append("")

        # Get stored items (this is a simplified check - in reality we'd need a separate field)
        # For now, just show message
        output.append("|yStored Items:|n")
        output.append("  (Item storage in bank coming soon)")

        output.append("|w" + "=" * 70 + "|n")
        self.caller.msg("\n".join(output))

    def _deposit(self, bank, currency):
        """Deposit gold or items."""
        if not self.args:
            self.caller.msg("Usage: bank/deposit <amount> gold  OR  bank/deposit <item name>")
            return

        args = self.args.strip()

        # Check if depositing gold
        if 'gold' in args.lower():
            try:
                amount = int(args.split()[0])
            except (ValueError, IndexError):
                self.caller.msg("Usage: bank/deposit <amount> gold")
                return

            if amount <= 0:
                self.caller.msg("Amount must be positive.")
                return

            if currency.gold < amount:
                self.caller.msg(f"You only have {currency.gold} gold.")
                return

            # Transfer gold
            currency.gold -= amount
            currency.save()
            bank.gold_stored += amount
            bank.save()

            self.caller.msg(f"|gYou deposit {amount} gold into the bank.|n")
            return

        # TODO: Implement item deposit
        self.caller.msg("Item deposit coming soon. For now, only gold can be deposited.")

    def _withdraw(self, bank, currency):
        """Withdraw gold or items."""
        if not self.args:
            self.caller.msg("Usage: bank/withdraw <amount> gold  OR  bank/withdraw <item name>")
            return

        args = self.args.strip()

        # Check if withdrawing gold
        if 'gold' in args.lower():
            try:
                amount = int(args.split()[0])
            except (ValueError, IndexError):
                self.caller.msg("Usage: bank/withdraw <amount> gold")
                return

            if amount <= 0:
                self.caller.msg("Amount must be positive.")
                return

            if bank.gold_stored < amount:
                self.caller.msg(f"You only have {bank.gold_stored} gold in the bank.")
                return

            # Transfer gold
            bank.gold_stored -= amount
            bank.save()
            currency.gold += amount
            currency.save()

            self.caller.msg(f"|gYou withdraw {amount} gold from the bank.|n")
            return

        # TODO: Implement item withdrawal
        self.caller.msg("Item withdrawal coming soon. For now, only gold can be withdrawn.")


class CmdCraft(Command):
    """
    Craft an item from materials.

    Usage:
      craft <item name>
      craft/list                     - List craftable items

    Attempts to craft an item if you have the required materials and skills.
    Success depends on your crafting skill and Intelligence.
    """

    key = "craft"
    aliases = []
    locks = "cmd:all()"
    help_category = "Inventory"

    def func(self):
        caller = self.caller

        if not hasattr(caller, 'db_character') or not caller.db_character:
            caller.msg("You don't have a character sheet.")
            return

        # List craftable items
        if 'list' in self.switches:
            self._list_craftable()
            return

        if not self.args:
            caller.msg("Usage: craft <item name>  OR  craft/list")
            return

        item_name = self.args.strip()

        # Find item template
        templates = ItemTemplate.objects.filter(
            required_materials__isnull=False
        ).exclude(required_materials={})

        # Try exact match
        template = None
        for tmpl in templates:
            if tmpl.name.lower() == item_name.lower():
                template = tmpl
                break

        # Try partial match
        if not template:
            for tmpl in templates:
                if item_name.lower() in tmpl.name.lower():
                    template = tmpl
                    break

        if not template:
            caller.msg(f"No craftable item named '{item_name}' found. Use 'craft/list' to see available items.")
            return

        # Check if in a workshop
        from world.witcher_rpg.room_models import WitcherRoom

        if not caller.location:
            caller.msg("|rYou must be in a location to craft.|n")
            return

        try:
            witcher_room = WitcherRoom.objects.get(room_object=caller.location)
        except WitcherRoom.DoesNotExist:
            caller.msg("|rThis location does not support crafting. You need a workshop in an urban area.|n")
            return

        # Attempt to craft
        result = CraftingSystem.attempt_craft(caller, template, witcher_room)

        if result['success']:
            caller.msg(f"|g{result['message']}|n")
            caller.msg(f"Roll result: {result['roll_result']['message']}")
            caller.msg(f"Difficulty: {result['difficulty_info']}")

            # Show material quality breakdown
            if result['material_details']:
                caller.msg("\n|yMaterial Quality Bonuses:|n")
                for mat in result['material_details']:
                    caller.msg(
                        f"  {mat['quantity']}x {mat['name']} ({mat['tier']}): "
                        f"-{mat['total_reduction']} CR"
                    )
        else:
            caller.msg(f"|r{result['message']}|n")
            if 'reasons' in result:
                for reason in result['reasons']:
                    caller.msg(f"  - {reason}")
            if 'roll_result' in result:
                caller.msg(f"Roll result: {result['roll_result']['message']}")
                if 'difficulty_info' in result:
                    caller.msg(f"Difficulty: {result['difficulty_info']}")

                # Show material quality breakdown even on failure
                if result.get('material_details'):
                    caller.msg("\n|yMaterial Quality Bonuses (attempted):|n")
                    for mat in result['material_details']:
                        caller.msg(
                            f"  {mat['quantity']}x {mat['name']} ({mat['tier']}): "
                            f"-{mat['total_reduction']} CR"
                        )

    def _list_craftable(self):
        """List all craftable items with material quality information."""
        templates = ItemTemplate.objects.filter(
            required_materials__isnull=False
        ).exclude(required_materials={}).order_by('tier', 'name')

        if not templates.exists():
            self.caller.msg("No craftable items found.")
            return

        output = []
        output.append("|w" + "=" * 70 + "|n")
        output.append("|w" + f"{'Craftable Items':^70}" + "|n")
        output.append("|w" + "=" * 70 + "|n")
        output.append("\n|cNote: Use high-quality materials to reduce crafting difficulty!|n")
        output.append("|cTier I: 0-2 CR/unit, Tier II: 3-7 CR/unit, Tier III: 8-15 CR/unit, Tier IV: 20-35 CR/unit|n")

        for template in templates:
            output.append(f"\n|y{template.name}|n ({template.get_tier_display()})")
            output.append(f"  Base Difficulty: CR {template.crafting_difficulty}")

            if template.required_materials:
                output.append("  Materials:")
                for mat_name, qty in template.required_materials.items():
                    # Get material template to show tier
                    mat_template = ItemTemplate.objects.filter(name=mat_name).first()
                    if mat_template:
                        tier_display = mat_template.get_tier_display()
                        quality_bonus = mat_template.material_quality_bonus
                        total_reduction = quality_bonus * qty
                        output.append(
                            f"    - {qty}x {mat_name} ({tier_display}, "
                            f"-{total_reduction} CR)"
                        )
                    else:
                        output.append(f"    - {qty}x {mat_name}")

            if template.crafting_skill_required:
                output.append(f"  Skill Required: {template.crafting_skill_required}")

        output.append("\n" + "|w" + "=" * 70 + "|n")
        self.caller.msg("\n".join(output))
