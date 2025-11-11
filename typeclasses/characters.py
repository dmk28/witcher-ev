"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

This module implements the model -> typeclass pattern for the Witcher RPG system.
The models (in world/witcher_rpg/models.py) store the data, and this typeclass
provides the behavior and methods.
"""

from evennia.objects.objects import DefaultCharacter
from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    pass


class WitcherCharacter(Character):
    """
    A Character with Witcher RPG mechanics.

    This typeclass provides methods for:
    - Rolling dice with exploding d10 mechanics
    - Making skill checks and stat checks
    - Displaying character information
    - Managing vocation feats and bonuses

    The actual character data is stored in the WitcherCharacter model
    (world/witcher_rpg/models.py), accessed via self.db_character.
    """

    @property
    def db_character(self):
        """
        Get the database character model for this character.

        Returns:
            WitcherCharacter: The model instance, or None if not yet created
        """
        try:
            return self.witcher_character
        except Exception:
            return None

    def at_object_creation(self):
        """
        Called only once, when the character is first created.
        We don't auto-create the WitcherCharacter model here - that should be
        done through the admin panel or a character creation command.
        """
        super().at_object_creation()
        self.db.desc = "A character in the Witcher universe."

    def get_stat(self, stat_name):
        """
        Get the effective value of a stat (including vocation modifiers).

        Args:
            stat_name (str): Name of the stat (e.g., 'strength', 'agility')

        Returns:
            int: The effective stat value, or 0 if character not set up
        """
        if not self.db_character:
            return 0
        return self.db_character.get_effective_stat(stat_name)

    def get_skill(self, skill_name):
        """
        Get the value of a skill.

        Args:
            skill_name (str): Name of the skill (e.g., 'blades', 'athletics')

        Returns:
            int: The skill value, or 0 if character not set up
        """
        if not self.db_character or not self.db_character.skills:
            return 0
        return getattr(self.db_character.skills, skill_name, 0)

    def has_skill_access(self, skill_name):
        """
        Check if this character has access to a special skill.

        Args:
            skill_name (str): Name of the skill

        Returns:
            bool: True if character has access
        """
        if not self.db_character:
            return False
        return self.db_character.has_skill_access(skill_name)

    def get_vocation_feats(self):
        """
        Get all feats for this character's vocation.

        Returns:
            QuerySet: Vocation feats, or empty list if no character
        """
        if not self.db_character:
            return []
        return self.db_character.get_vocation_feats()

    def calculate_dice_pool(self, stat_name, skill_name=None, bonus_dice=0):
        """
        Calculate the number of dice to roll for a check.

        Args:
            stat_name (str): The stat to use (e.g., 'strength')
            skill_name (str, optional): The skill to add (e.g., 'blades')
            bonus_dice (int): Additional bonus dice

        Returns:
            int: Total number of dice to roll
        """
        dice_pool = self.get_stat(stat_name)

        if skill_name:
            dice_pool += self.get_skill(skill_name)

        dice_pool += bonus_dice

        return max(dice_pool, 1)  # Minimum 1 die

    def roll_check(self, stat_name, skill_name=None, difficulty=None,
                   bonus_dice=0, show_to_room=False):
        """
        Perform a dice roll check.

        Args:
            stat_name (str): The stat to roll (e.g., 'strength')
            skill_name (str, optional): The skill to add
            difficulty (int, optional): Fixed difficulty, or None for simple roll
            bonus_dice (int): Bonus dice to add
            show_to_room (bool): Whether to show result to entire room

        Returns:
            dict: Roll result with success/failure information
        """
        from world.witcher_rpg.dice import DiceRoller, ChallengeResolver

        # Calculate dice pool
        dice_pool = self.calculate_dice_pool(stat_name, skill_name, bonus_dice)

        # Perform the roll
        if difficulty is not None:
            result = ChallengeResolver.fixed_difficulty_check(dice_pool, difficulty)
            message = ChallengeResolver.format_challenge_result(result, 'fixed')
        else:
            result = DiceRoller.roll_multiple_d10(dice_pool)
            message = DiceRoller.format_roll_result(result)

        # Build context message
        context_parts = [stat_name.title()]
        if skill_name:
            context_parts.append(skill_name.title())
        context = f"{' + '.join(context_parts)} ({dice_pool}d10)"

        full_message = f"|c{self.name}|n rolls |w{context}|n:\n{message}"

        # Display the result
        if show_to_room:
            self.location.msg_contents(full_message)
        else:
            self.msg(full_message)

        return result

    def display_sheet(self):
        """
        Display the character sheet.

        Returns:
            str: Formatted character sheet
        """
        if not self.db_character:
            return "|rThis character has not been set up with Witcher RPG stats yet.|n"

        char = self.db_character
        lines = []

        # Header
        lines.append(f"|c{'=' * 70}|n")
        lines.append(f"|w{char.character_name.center(70)}|n")
        lines.append(f"|c{'=' * 70}|n")

        # Basic info
        lines.append(f"|wVocation:|n {char.vocation}")
        lines.append(f"|wRace:|n {char.get_race_display()}")
        if char.country:
            lines.append(f"|wCountry:|n {char.country.get_name_display()} (+1 {char.country.bonus_stat.title()})")
        if char.witcher_style != 'none':
            lines.append(f"|wWitcher Style:|n {char.get_witcher_style_display()}")
        lines.append(f"|wExperience:|n {char.experience_points} XP")

        # Show race/style bonuses
        race_mods = char.get_race_modifiers()
        if race_mods['magic_cr_modifier'] != 0 or race_mods['damage_taken_modifier'] != 1.0:
            lines.append(f"|wRacial Traits:|n {race_mods['description']}")

        if char.witcher_style != 'none' and char.vocation.name == 'witcher':
            style_bonuses = char.get_witcher_style_bonuses()
            if style_bonuses:
                lines.append(f"|wStyle:|n {style_bonuses['description']}")

        lines.append("")

        # Stats (including all bonuses: vocation + witcher style)
        lines.append("|y--- Stats (with All Bonuses) ---|n")

        # Physical
        lines.append(
            f"|gPhysical:|n STR: {char.get_total_effective_stat('strength'):2d}  "
            f"AGI: {char.get_total_effective_stat('agility'):2d}  "
            f"END: {char.get_total_effective_stat('endurance'):2d}  "
            f"REF: {char.get_total_effective_stat('reflexes'):2d}"
        )

        # Mental
        lines.append(
            f"|gMental:|n   WIT: {char.get_total_effective_stat('wit'):2d}  "
            f"INT: {char.get_total_effective_stat('intelligence'):2d}  "
            f"WIL: {char.get_total_effective_stat('willpower'):2d}  "
            f"PER: {char.get_total_effective_stat('perception'):2d}"
        )

        # Social
        lines.append(
            f"|gSocial:|n   CHA: {char.get_total_effective_stat('charm'):2d}  "
            f"APP: {char.get_total_effective_stat('appearance'):2d}  "
            f"GRA: {char.get_total_effective_stat('graces'):2d}  "
            f"CUN: {char.get_total_effective_stat('cunning'):2d}"
        )
        lines.append("")

        # Skills
        lines.append("|y--- Skills ---|n")
        skills = char.skills

        combat_skills = [
            ('Blades', skills.blades),
            ('Axes', skills.axes),
            ('Maces', skills.maces),
            ('Spears', skills.spears),
            ('Crossbows', skills.crossbows),
            ('Brawling', skills.brawling)
        ]
        lines.append("|gCombat:|n " + "  ".join(f"{name}: {val}" for name, val in combat_skills))

        special_skills = []
        if char.has_skill_access('alchemy'):
            special_skills.append(f"Alchemy: {skills.alchemy}")
        if char.has_skill_access('magery'):
            special_skills.append(f"Magery: {skills.magery}")
        if char.has_skill_access('sign_sorcery'):
            special_skills.append(f"Sign Sorcery: {skills.sign_sorcery}")

        if special_skills:
            lines.append("|gSpecial:|n " + "  ".join(special_skills))

        if skills.crafting_type != 'none':
            lines.append(f"|gCrafting:|n {skills.get_crafting_type_display()}: {skills.crafting_skill}")

        lines.append(f"|gGeneral:|n Athletics: {skills.athletics}")

        # Support skills (if any are non-zero)
        support_skills = []
        if skills.resistance > 0:
            support_skills.append(f"Resistance: {skills.resistance}")
        if skills.leadership > 0:
            support_skills.append(f"Leadership: {skills.leadership}")
        if skills.tactics > 0:
            support_skills.append(f"Tactics: {skills.tactics}")

        if support_skills:
            lines.append("|gSupport:|n " + "  ".join(support_skills))

        lines.append("")

        # Combat Stats
        lines.append("|y--- Combat Stats ---|n")

        # Calculate combat-related values
        max_hp = char.get_total_effective_stat('endurance') * 10
        initiative_bonus = (
            char.get_total_effective_stat('reflexes') +
            char.get_total_effective_stat('perception')
        )

        lines.append(f"|gMax HP:|n {max_hp} (Endurance × 10)")
        lines.append(f"|gInitiative Bonus:|n +{initiative_bonus} (Reflexes + Perception)")

        # Show racial combat modifiers
        if race_mods['damage_taken_modifier'] != 1.0:
            damage_percent = int(race_mods['damage_taken_modifier'] * 100)
            lines.append(f"|gDamage Taken:|n {damage_percent}% of normal")

        if race_mods['magic_cr_modifier'] != 0:
            modifier_str = f"{race_mods['magic_cr_modifier']:+d}"
            lines.append(f"|gSpell CR Modifier:|n {modifier_str}")

        lines.append("")

        # Vocation Feats
        feats = char.get_vocation_feats()
        if feats:
            lines.append("|y--- Vocation Feats ---|n")
            for feat in feats:
                feat_desc = f"|g{feat.name}:|n {feat.description}"
                if feat.bonus_dice and feat.bonus_stat:
                    feat_desc += f" |y(+{feat.bonus_dice}d to {feat.bonus_stat})|n"
                if feat.trigger_condition:
                    feat_desc += f" |c[{feat.trigger_condition}]|n"
                lines.append(feat_desc)

        # Special Witcher appearance mechanic
        if char.vocation.name == 'witcher':
            if not feats:
                lines.append("|y--- Vocation Feats ---|n")
            lines.append(
                "|gWitcher Mystique:|n +3 Appearance for seduction rolls vs females. "
                "|c[Lore-accurate: mutations make Witchers strangely attractive]|n"
            )

        if feats or char.vocation.name == 'witcher':
            lines.append("")

        lines.append(f"|c{'=' * 70}|n")

        return "\n".join(lines)

    def return_appearance(self, looker, **kwargs):
        """
        This is called when someone looks at this character.
        """
        # Get the base appearance
        text = super().return_appearance(looker, **kwargs)

        # Add character sheet if they have one
        if self.db_character:
            text += "\n\n" + self.display_sheet()

        return text
