"""
Crafting Commands for Witcher RPG

Allows players to view recipes, learn recipes, craft items, and view set bonuses.
"""

from evennia import Command
from django.utils import timezone
from world.witcher_rpg.crafting_models import (
    CraftingRecipe,
    ItemSet,
    LearnedRecipe,
    CraftingAttempt,
    VocationSkillCostMultiplier
)
from world.witcher_rpg.models import WitcherCharacter
import random


class CmdRecipes(Command):
    """
    View your learned crafting recipes.

    Usage:
      recipes
      recipes <crafting_type>
      recipes weaponsmithing

    Shows all recipes you've learned. Optionally filter by crafting type:
    weaponsmithing, armorsmithing, alchemy, runecrafting, jewelcrafting, tailoring

    For each recipe, displays:
    - Name and rarity
    - Skill requirement and difficulty
    - Required materials
    - Time and costs
    - Times you've crafted it
    """

    key = "recipes"
    aliases = ["recipelist", "myrecipes"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller

        # Get character
        try:
            character = WitcherCharacter.objects.get(character=caller)
        except WitcherCharacter.DoesNotExist:
            caller.msg("You don't have a character yet. Create one first!")
            return

        # Get learned recipes
        learned_recipes = LearnedRecipe.objects.filter(
            character=caller
        ).select_related('recipe', 'recipe__set_piece')

        if not learned_recipes.exists():
            caller.msg("You haven't learned any crafting recipes yet.")
            caller.msg("\nRecipes can be learned from:")
            caller.msg("  - Purchasing from master craftsmen")
            caller.msg("  - Finding diagrams in the world")
            caller.msg("  - Completing quests")
            caller.msg("  - GM rewards")
            return

        # Filter by crafting type if specified
        crafting_type = self.args.strip().lower() if self.args else None
        if crafting_type:
            learned_recipes = learned_recipes.filter(
                recipe__crafting_type=crafting_type
            )
            if not learned_recipes.exists():
                caller.msg(f"You haven't learned any {crafting_type} recipes.")
                return

        # Build output
        lines = []
        lines.append("=" * 70)
        if crafting_type:
            lines.append(f"Your {crafting_type.title()} Recipes")
        else:
            lines.append("Your Learned Crafting Recipes")
        lines.append("=" * 70)

        # Group by crafting type
        by_type = {}
        for learned in learned_recipes:
            recipe_type = learned.recipe.crafting_type
            if recipe_type not in by_type:
                by_type[recipe_type] = []
            by_type[recipe_type].append(learned)

        for recipe_type, recipes_list in sorted(by_type.items()):
            lines.append(f"\n|c{recipe_type.upper()}|n")
            lines.append("-" * 70)

            for learned in recipes_list:
                recipe = learned.recipe

                # Name and rarity
                rarity = "|y(RARE)|n" if recipe.is_rare else ""
                set_marker = "|g[SET]|n" if recipe.set_piece else ""
                lines.append(f"\n|w{recipe.name}|n {rarity} {set_marker}")

                # Requirements
                lines.append(
                    f"  Skill: {recipe.min_skill_level}+  |  "
                    f"CR: {recipe.base_difficulty}  |  "
                    f"Time: {recipe.time_required_minutes} min  |  "
                    f"Cost: {recipe.gold_cost} crowns"
                )

                # Materials
                materials = ", ".join(
                    f"{mat} x{qty}"
                    for mat, qty in recipe.required_materials.items()
                )
                lines.append(f"  Materials: {materials}")

                # Workshop and rewards
                lines.append(
                    f"  Workshop: {recipe.required_workshop}  |  "
                    f"XP Reward: {recipe.xp_reward}  |  "
                    f"Crafted: {learned.times_crafted} times"
                )

                # Set piece info
                if recipe.set_piece:
                    lines.append(f"  Set: |g{recipe.set_piece.name}|n (Tier {recipe.set_piece.tier})")

        lines.append("\n" + "=" * 70)
        lines.append("Use |wcraft <recipe name>|n to craft an item")
        lines.append("Use |wsetbonus|n to view your current set bonuses")
        lines.append("=" * 70)

        caller.msg("\n".join(lines))


class CmdCraft(Command):
    """
    Craft an item from a learned recipe.

    Usage:
      craft <recipe name>
      craft Moonblade Silver Sword Formula
      craft Superior Swallow Potion

    Attempts to craft an item from one of your learned recipes.

    Requirements:
    - You must have learned the recipe
    - Your crafting skill must meet the minimum
    - You must have all required materials
    - You must be at the appropriate workshop
    - You must have gold for workshop fees

    The crafting check is:
      1d10 + skill level + stat modifier + bonuses vs. CR

    Material quality reduces difficulty:
    - Tier II materials: -10 CR
    - Tier III materials: -20 CR
    - Tier IV materials: -30 CR

    Success: Item created, XP gained, materials consumed
    Failure: No item, materials consumed (or 50% if Artisan with Quality Control)
    """

    key = "craft"
    aliases = ["craftitem"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: craft <recipe name>")
            return

        recipe_name = self.args.strip()

        # Get character
        try:
            character = WitcherCharacter.objects.get(character=caller)
        except WitcherCharacter.DoesNotExist:
            caller.msg("You don't have a character yet. Create one first!")
            return

        # Check if recipe is learned
        try:
            learned = LearnedRecipe.objects.select_related(
                'recipe', 'recipe__set_piece'
            ).get(
                character=caller,
                recipe__name__iexact=recipe_name
            )
        except LearnedRecipe.DoesNotExist:
            caller.msg(f"You haven't learned the recipe '{recipe_name}'.")
            caller.msg("Use |wrecipes|n to see your learned recipes.")
            return

        recipe = learned.recipe

        # Check skill level
        crafting_skill = getattr(character.skills, 'crafting_skill', 0)
        if crafting_skill < recipe.min_skill_level:
            caller.msg(
                f"|rInsufficient skill!|n\n"
                f"Your crafting skill: {crafting_skill}\n"
                f"Required: {recipe.min_skill_level}"
            )
            return

        # Check gold
        if character.gold < recipe.gold_cost:
            caller.msg(
                f"|rInsufficient gold!|n\n"
                f"Your gold: {character.gold}\n"
                f"Required: {recipe.gold_cost} crowns"
            )
            return

        # TODO: Check for materials in inventory
        # TODO: Check for workshop location
        # For now, we'll assume materials and workshop are available

        # Calculate difficulty
        # For now, assume Tier II materials (-10 CR)
        material_quality = 2  # TODO: Calculate from actual materials
        adjusted_difficulty = recipe.calculate_adjusted_difficulty(material_quality)

        # Apply Artisan Master Craftsman feat (-10 CR, +2 to roll)
        is_artisan = False
        artisan_bonus = 0
        try:
            vocation = character.vocation
            if vocation and vocation.name == 'artisan':
                is_artisan = True
                adjusted_difficulty -= 10  # Master Craftsman reduces CR
                artisan_bonus = 2  # +2 to roll
        except:
            pass

        # Make crafting check
        roll = random.randint(1, 10)
        stat_mod = getattr(character.stats, 'intelligence', 0)
        total = roll + crafting_skill + stat_mod + artisan_bonus

        success = total >= adjusted_difficulty

        # Build result message
        lines = []
        lines.append("=" * 70)
        lines.append(f"Crafting: {recipe.name}")
        lines.append("=" * 70)
        lines.append(f"Skill: {crafting_skill}  |  Base CR: {recipe.base_difficulty}")
        lines.append(f"Material Quality: Tier {material_quality} (-{(material_quality - 1) * 10} CR)")
        if is_artisan:
            lines.append(f"Master Craftsman: -10 CR, +2 to roll")
        lines.append(f"Final CR: {adjusted_difficulty}")
        lines.append("")
        lines.append(f"Roll: {roll}")
        lines.append(f"Skill: +{crafting_skill}")
        lines.append(f"Intelligence: +{stat_mod}")
        if artisan_bonus:
            lines.append(f"Artisan Bonus: +{artisan_bonus}")
        lines.append(f"Total: |w{total}|n vs CR {adjusted_difficulty}")
        lines.append("")

        if success:
            lines.append("|gSUCCESS!|n")
            lines.append(f"You successfully craft {recipe.name}!")
            lines.append(f"XP Gained: +{recipe.xp_reward}")

            # Grant XP
            character.xp += recipe.xp_reward
            character.save()

            # Increment craft count
            learned.times_crafted += 1
            learned.save()

            # Deduct gold
            character.gold -= recipe.gold_cost
            character.save()

            # Log attempt
            CraftingAttempt.objects.create(
                character=caller,
                recipe=recipe,
                success=True,
                roll_result=total,
                difficulty=adjusted_difficulty,
                materials_used=recipe.required_materials,
                xp_gained=recipe.xp_reward
            )

            # TODO: Create actual item and add to inventory

        else:
            lines.append("|rFAILURE!|n")
            lines.append(f"Your crafting attempt failed.")

            if is_artisan:
                lines.append("|yQuality Control:|n Materials only 50% consumed!")
            else:
                lines.append("Materials consumed with no result.")

            # Deduct gold (workshop fees)
            character.gold -= recipe.gold_cost
            character.save()

            # Log attempt
            CraftingAttempt.objects.create(
                character=caller,
                recipe=recipe,
                success=False,
                roll_result=total,
                difficulty=adjusted_difficulty,
                materials_used=recipe.required_materials,
                xp_gained=0
            )

            # TODO: Consume materials from inventory (50% for artisan, 100% for others)

        lines.append("=" * 70)
        caller.msg("\n".join(lines))


class CmdLearnRecipe(Command):
    """
    Learn a new crafting recipe (GM command).

    Usage:
      learnrecipe <character> = <recipe name>
      learnrecipe Geralt = Moonblade Silver Sword Formula

    Grants a character knowledge of a crafting recipe.

    This is a GM command. Players learn recipes through:
    - Purchasing from NPCs
    - Finding diagrams in the world
    - Quest rewards
    - Training with master craftsmen
    """

    key = "learnrecipe"
    aliases = ["grantrecipe", "teachrecipe"]
    locks = "cmd:perm(Builder)"
    help_category = "GM"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: learnrecipe <character> = <recipe name>")
            return

        char_name, recipe_name = [x.strip() for x in self.args.split("=", 1)]

        # Find character
        char_obj = self.caller.search(char_name, global_search=True)
        if not char_obj:
            return

        # Find recipe
        try:
            recipe = CraftingRecipe.objects.get(name__iexact=recipe_name)
        except CraftingRecipe.DoesNotExist:
            self.caller.msg(f"Recipe '{recipe_name}' not found.")
            self.caller.msg("Check /admin/ for available recipes.")
            return

        # Check if already learned
        if LearnedRecipe.objects.filter(character=char_obj, recipe=recipe).exists():
            self.caller.msg(f"{char_obj.name} already knows {recipe.name}.")
            return

        # Grant recipe
        LearnedRecipe.objects.create(
            character=char_obj,
            recipe=recipe
        )

        # Notify
        self.caller.msg(f"|gGranted recipe:|n {recipe.name} to {char_obj.name}")
        char_obj.msg(
            f"|gYou have learned a new recipe:|n {recipe.name}\n"
            f"Use |wrecipes|n to view your learned recipes."
        )


class CmdSetBonus(Command):
    """
    View set bonuses from your equipped items.

    Usage:
      setbonus
      setbonus <set name>
      setbonus Cat School Gear

    Shows which item sets you're wearing pieces of and what bonuses
    are currently active.

    Set bonuses are cumulative:
    - 2 pieces: First bonus tier
    - 3 pieces: First + Second bonus tier
    - 4 pieces: First + Second + Third bonus tier
    - 5 pieces: All bonus tiers (maximum power)

    Without arguments, shows all your currently active set bonuses.
    With a set name, shows detailed information about that specific set.
    """

    key = "setbonus"
    aliases = ["sets", "itemsets"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller

        # Get all available sets
        if self.args:
            # Show details for specific set
            set_name = self.args.strip()
            try:
                item_set = ItemSet.objects.get(name__iexact=set_name)
            except ItemSet.DoesNotExist:
                caller.msg(f"Item set '{set_name}' not found.")
                return

            self._show_set_details(item_set)
        else:
            # Show all sets and current bonuses
            self._show_current_bonuses()

    def _show_set_details(self, item_set):
        """Show detailed information about a specific set."""
        lines = []
        lines.append("=" * 70)
        lines.append(f"{item_set.name} (Tier {item_set.tier})")
        lines.append("=" * 70)
        lines.append(f"Type: {item_set.get_set_type_display()}")
        lines.append("")
        lines.append(item_set.description)
        lines.append("")
        lines.append("|wSet Bonuses:|n")
        lines.append("-" * 70)

        # Show bonuses for each threshold
        if item_set.two_piece_bonus:
            lines.append(
                f"|c2-Piece:|n {item_set.two_piece_bonus.get('description', 'Bonus active')}"
            )

        if item_set.three_piece_bonus:
            lines.append(
                f"|c3-Piece:|n {item_set.three_piece_bonus.get('description', 'Bonus active')}"
            )

        if item_set.four_piece_bonus:
            lines.append(
                f"|c4-Piece:|n {item_set.four_piece_bonus.get('description', 'Bonus active')}"
            )

        if item_set.five_piece_bonus:
            lines.append(
                f"|c5-Piece:|n {item_set.five_piece_bonus.get('description', 'Bonus active')}"
            )

        lines.append("=" * 70)
        lines.append("\nRecipes for this set:")

        # Show recipes that create set pieces
        recipes = CraftingRecipe.objects.filter(set_piece=item_set)
        if recipes.exists():
            for recipe in recipes:
                lines.append(f"  - {recipe.name} (Skill {recipe.min_skill_level}+)")
        else:
            lines.append("  No recipes available yet")

        lines.append("=" * 70)

        self.caller.msg("\n".join(lines))

    def _show_current_bonuses(self):
        """Show currently active set bonuses."""
        # TODO: Implement actual inventory checking for worn items
        # For now, show all available sets

        lines = []
        lines.append("=" * 70)
        lines.append("Item Sets & Bonuses")
        lines.append("=" * 70)
        lines.append("\nCurrently Equipped Set Pieces: |yNONE|n")
        lines.append("(Inventory system not yet implemented)")
        lines.append("")
        lines.append("|wAvailable Item Sets:|n")
        lines.append("-" * 70)

        sets = ItemSet.objects.all().order_by('tier', 'name')

        if not sets.exists():
            lines.append("No item sets available yet.")
        else:
            for item_set in sets:
                bonus_count = sum([
                    bool(item_set.two_piece_bonus),
                    bool(item_set.three_piece_bonus),
                    bool(item_set.four_piece_bonus),
                    bool(item_set.five_piece_bonus)
                ])

                lines.append(
                    f"|w{item_set.name}|n - Tier {item_set.tier} - "
                    f"{item_set.get_set_type_display()} ({bonus_count} bonus tiers)"
                )

        lines.append("")
        lines.append("=" * 70)
        lines.append("Use |wsetbonus <set name>|n to view detailed set bonuses")
        lines.append("=" * 70)

        self.caller.msg("\n".join(lines))


class CmdCraftingHistory(Command):
    """
    View your crafting history.

    Usage:
      crafthistory
      crafthistory <recipe name>

    Shows your past crafting attempts with success/failure rates.
    Optionally filter by recipe name to see history for a specific recipe.
    """

    key = "crafthistory"
    aliases = ["crafthist", "craftinglog"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller

        # Get character
        try:
            character = WitcherCharacter.objects.get(character=caller)
        except WitcherCharacter.DoesNotExist:
            caller.msg("You don't have a character yet. Create one first!")
            return

        # Get crafting attempts
        attempts = CraftingAttempt.objects.filter(
            character=caller
        ).select_related('recipe').order_by('-timestamp')

        # Filter by recipe if specified
        if self.args:
            recipe_name = self.args.strip()
            attempts = attempts.filter(recipe__name__icontains=recipe_name)

        if not attempts.exists():
            if self.args:
                caller.msg(f"No crafting attempts found for '{self.args}'.")
            else:
                caller.msg("You haven't attempted any crafting yet.")
            return

        # Calculate statistics
        total = attempts.count()
        successful = attempts.filter(success=True).count()
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        total_xp = sum(a.xp_gained for a in attempts)

        # Build output
        lines = []
        lines.append("=" * 70)
        if self.args:
            lines.append(f"Crafting History: {self.args}")
        else:
            lines.append("Your Crafting History")
        lines.append("=" * 70)
        lines.append(
            f"Total Attempts: {total}  |  "
            f"Success: |g{successful}|n  |  "
            f"Failed: |r{failed}|n  |  "
            f"Success Rate: {success_rate:.1f}%"
        )
        lines.append(f"Total XP Earned: |y{total_xp}|n")
        lines.append("")

        # Show recent attempts (limit to 20)
        lines.append("|wRecent Attempts:|n")
        lines.append("-" * 70)

        for attempt in attempts[:20]:
            status = "|gSUCCESS|n" if attempt.success else "|rFAILURE|n"
            date = attempt.timestamp.strftime("%Y-%m-%d %H:%M")

            lines.append(
                f"{date} | {status} | {attempt.recipe.name} "
                f"(Roll: {attempt.roll_result} vs CR {attempt.difficulty})"
            )
            if attempt.success:
                lines.append(f"  XP Gained: +{attempt.xp_gained}")

        if attempts.count() > 20:
            lines.append(f"\n... and {attempts.count() - 20} more attempts")

        lines.append("=" * 70)

        caller.msg("\n".join(lines))
