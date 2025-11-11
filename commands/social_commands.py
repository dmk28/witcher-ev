"""
Social Combat Commands for Witcher RPG

Commands for the Intrigue system where characters use social stats
to undermine opponents and gain material rewards.
"""

from evennia import Command
from world.witcher_rpg.social_models import SocialEncounter, SocialParticipant, SocialAction
from world.witcher_rpg.social_combat import SocialCombatResolver, SocialEncounterManager


class CmdSocialStart(Command):
    """
    Start a social combat/intrigue encounter.

    Usage:
        intrigue <target> [type] [stakes]
        seduce <target> [stakes]
        negotiate <target> [stakes]
        intimidate <target> [stakes]

    Types:
        seduction - Use charm and appearance to win over the target
        negotiation - Use cunning and graces to make deals
        intimidation - Use presence to cow the opponent
        debate - Use wit to win arguments
        manipulation - Use cunning to trick and control

    Examples:
        intrigue Lord Vogler negotiation
        seduce Duchess Anna "expensive gift"
        negotiate Merchant Zdenek "better prices"
        intimidate Guard "information about the baron"

    This starts social combat where you can use charm, cunning, appearance,
    and graces to defeat opponents and gain rewards (gold, favors, items).
    """

    key = "intrigue"
    aliases = ["seduce", "negotiate", "intimidate"]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: intrigue <target> [type] [stakes]")
            return

        # Parse arguments
        args_list = self.args.strip().split(None, 2)
        target_name = args_list[0]
        encounter_type = args_list[1] if len(args_list) > 1 else None
        stakes_desc = args_list[2] if len(args_list) > 2 else None

        # Determine encounter type
        if self.cmdname in ["seduce", "seduction"]:
            encounter_type = "seduction"
        elif self.cmdname == "negotiate":
            encounter_type = "negotiation"
        elif self.cmdname == "intimidate":
            encounter_type = "intimidation"
        elif not encounter_type:
            encounter_type = "negotiation"

        # Find target
        target = caller.search(target_name)
        if not target:
            return

        # Check if already in social combat
        location = caller.location
        existing_encounter = SocialEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if existing_encounter:
            caller.msg("There is already an active social encounter here!")
            return

        # Check if target has character data
        if not hasattr(target, 'db_character') or not target.db_character:
            caller.msg(f"{target.name} is not set up for social combat.")
            return

        # Create encounter
        stakes = {'description': stakes_desc} if stakes_desc else {}
        encounter = SocialEncounterManager.create_encounter(
            location=location,
            encounter_type=encounter_type,
            stakes=stakes
        )

        # Add participants
        caller_participant = SocialEncounterManager.add_participant(
            encounter, caller, wealth_level=2
        )

        # Determine target wealth level based on social rank
        target_rank = getattr(target.db_character, 'social_rank', 2)
        wealth_map = {1: 1, 2: 2, 3: 4, 4: 5, 5: 6}
        target_wealth = wealth_map.get(target_rank, 2)

        target_participant = SocialEncounterManager.add_participant(
            encounter, target, wealth_level=target_wealth
        )

        # Announce start
        location.msg_contents(
            f"|y{'=' * 70}|n\n"
            f"|c{caller.name}|n initiates |y{encounter_type}|n with |c{target.name}|n!\n"
            f"|y{'=' * 70}|n"
        )

        # Show initiative order
        participants = encounter.participants.all().order_by('initiative_order')
        location.msg_contents("\n|wInitiative Order:|n")
        for p in participants:
            capital_bar = self._make_capital_bar(p.current_social_capital, p.max_social_capital)
            location.msg_contents(
                f"  {p.initiative_order + 1}. |c{p.character.name}|n "
                f"(Initiative: {p.initiative_roll}) "
                f"- Social Capital: {capital_bar}"
            )

        # Show whose turn it is
        current = encounter.get_current_participant()
        if current:
            location.msg_contents(
                f"\n|yIt is |c{current.character.name}|y's turn.|n\n"
                f"Use |wsocial <action> <target>|n or |wsocialstance <stance>|n"
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


class CmdSocialAction(Command):
    """
    Perform a social action in an intrigue encounter.

    Usage:
        social <action> [target]
        social charm duchess
        social undermine lord
        social flatter

    Common Actions:
        charm - Use charm to win favor (Charm based)
        flatter - Use appearance and grace to please (Appearance + Graces)
        undermine - Use cunning to weaken opponent (Cunning based)
        manipulate - Use cunning to control (Cunning based)
        seduce - Use appearance and charm (Appearance + Charm)
        intimidate - Use presence to cow (Charm + Cunning)

    Use 'social list' to see all available actions for your current stance
    and encounter type.
    """

    key = "social"
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        location = caller.location

        # Find active encounter
        encounter = SocialEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if not encounter:
            caller.msg("There is no active social encounter here.")
            return

        # Find caller's participant
        try:
            actor_participant = encounter.participants.get(character=caller)
        except SocialParticipant.DoesNotExist:
            caller.msg("You are not part of this social encounter.")
            return

        # Check if it's caller's turn
        current_participant = encounter.get_current_participant()
        if current_participant != actor_participant:
            caller.msg(f"It's not your turn. It is {current_participant.character.name}'s turn.")
            return

        if not self.args:
            caller.msg("Usage: social <action> [target]")
            return

        args_list = self.args.strip().split(None, 1)
        action_name = args_list[0].lower()

        # Handle 'list' command
        if action_name == "list":
            self._list_actions(encounter, actor_participant)
            return

        # Find the action
        try:
            action = SocialAction.objects.get(name__iexact=action_name)
        except SocialAction.DoesNotExist:
            caller.msg(f"Unknown action '{action_name}'. Use 'social list' to see available actions.")
            return

        # Check if action can be used
        if not action.can_use_in_encounter(encounter.encounter_type, actor_participant.stance):
            caller.msg(
                f"You cannot use {action.name} with your current stance "
                f"({actor_participant.stance}) in this type of encounter."
            )
            return

        # Find target
        if action.action_type in ['attack', 'undermine']:
            # These actions need a target
            if len(args_list) < 2:
                caller.msg(f"{action.name} requires a target.")
                return

            target = caller.search(args_list[1])
            if not target:
                return

            try:
                target_participant = encounter.participants.get(character=target)
            except SocialParticipant.DoesNotExist:
                caller.msg(f"{target.name} is not in this encounter.")
                return

            if target_participant == actor_participant:
                caller.msg("You cannot target yourself with this action.")
                return

        else:
            # Support/boost actions default to self if no target specified
            if len(args_list) >= 2:
                target = caller.search(args_list[1])
                if not target:
                    return
                try:
                    target_participant = encounter.participants.get(character=target)
                except SocialParticipant.DoesNotExist:
                    caller.msg(f"{target.name} is not in this encounter.")
                    return
            else:
                target = caller
                target_participant = actor_participant

        # Perform the action
        result = SocialCombatResolver.perform_social_action(
            actor_participant,
            target_participant,
            action,
            encounter
        )

        # Format and display result
        message = SocialCombatResolver.format_social_action_result(
            caller, target, action, result
        )
        location.msg_contents(message)

        # Check if encounter should end
        active_opponents = encounter.participants.filter(
            is_active=True
        ).exclude(character=caller).count()

        if active_opponents == 0:
            # Caller wins!
            end_result = SocialEncounterManager.end_encounter(encounter, actor_participant)
            self._announce_victory(location, caller, end_result)
            return

        # Advance turn
        encounter.advance_turn()
        next_participant = encounter.get_current_participant()

        if next_participant:
            location.msg_contents(
                f"\n|yIt is now |c{next_participant.character.name}|y's turn.|n"
            )

    def _list_actions(self, encounter, participant):
        """List available actions for the participant."""
        available = SocialEncounterManager.get_available_actions(participant, encounter)

        if not available:
            self.caller.msg("No actions available.")
            return

        lines = ["|y=== Available Social Actions ===|n"]
        for action in available:
            stat_info = action.primary_stat.title()
            if action.secondary_stat and action.secondary_stat != 'none':
                stat_info += f" + {action.secondary_stat.title()}"

            lines.append(
                f"|w{action.name}|n ({action.get_action_type_display()}) "
                f"- {stat_info} vs CR {action.base_difficulty}"
            )
            lines.append(f"  {action.description}")

        self.caller.msg("\n".join(lines))

    def _announce_victory(self, location, winner, results):
        """Announce the end of the encounter and rewards."""
        from world.witcher_rpg.shop_system import ShopManager

        lines = [
            f"\n|y{'=' * 70}|n",
            f"|gSocial Encounter Complete!|n",
            f"|c{winner.name}|n has emerged victorious!",
            f"|y{'=' * 70}|n"
        ]

        # Check if this was a shop haggling encounter
        shop = ShopManager.get_shop_at_location(location)
        if shop and shop.merchant:
            # Check if merchant was defeated
            defeated_names = [name.lower() for name in results.get('defeated', [])]
            if shop.merchant.name.lower() in defeated_names:
                # Apply shop discount
                from world.witcher_rpg.social_models import SocialParticipant
                try:
                    winner_participant = SocialParticipant.objects.filter(
                        character=winner
                    ).order_by('-encounter__created_at').first()

                    if winner_participant:
                        victory_margin = winner_participant.current_social_capital
                        discount_result = ShopManager.apply_social_combat_discount(
                            shop, winner, victory_margin
                        )

                        # Store discount in temporary attribute
                        winner.ndb.shop_discount = discount_result['discount_percentage']

                        lines.append(f"\n|g=== Haggling Success! ===|n")
                        lines.append(discount_result['message'])
                        lines.append(f"|yUse 'buy' or 'sell' now to apply your discount!|n")
                except Exception:
                    pass

        if results.get('rewards'):
            lines.append("\n|g=== Rewards Gained ===|n")
            for reward in results['rewards']:
                lines.append(f"From |c{reward['from']}|n:")
                if reward['gold'] > 0:
                    lines.append(f"  • {reward['gold']} crowns")
                if reward['item_tier']:
                    lines.append(f"  • {reward['item_tier']} item")
                if reward['favor_level'] > 0:
                    lines.append(f"  • Level {reward['favor_level']} favor")

        location.msg_contents("\n".join(lines))


class CmdSocialStance(Command):
    """
    Change your social stance during intrigue.

    Usage:
        socialstance <stance>
        stance <stance>

    Stances:
        charming - Emphasize appeal and likability (+2d Charm, +1d Appearance)
        cunning - Use wit and manipulation (+2d Cunning, +1d Graces)
        bold - Direct and assertive approach (+1d Charm, -5 CR on Cunning)
        subtle - Indirect and measured (+2d Graces, +1d Cunning)

    Your stance affects which actions are available and provides bonuses
    to certain stats.
    """

    key = "socialstance"
    aliases = ["stance"]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        location = caller.location

        # Find active encounter
        encounter = SocialEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if not encounter:
            caller.msg("There is no active social encounter here.")
            return

        # Find caller's participant
        try:
            participant = encounter.participants.get(character=caller)
        except SocialParticipant.DoesNotExist:
            caller.msg("You are not part of this social encounter.")
            return

        if not self.args:
            caller.msg(
                f"Your current stance is: |w{participant.stance}|n\n"
                f"Available stances: charming, cunning, bold, subtle"
            )
            return

        stance = self.args.strip().lower()
        valid_stances = ['charming', 'cunning', 'bold', 'subtle']

        if stance not in valid_stances:
            caller.msg(f"Invalid stance. Choose from: {', '.join(valid_stances)}")
            return

        old_stance = participant.stance
        participant.stance = stance
        participant.save()

        caller.msg(f"You shift from {old_stance} to |w{stance}|n stance.")
        location.msg_contents(
            f"|c{caller.name}|n adopts a |w{stance}|n approach.",
            exclude=[caller]
        )


class CmdSocialStatus(Command):
    """
    View the status of the current social encounter.

    Usage:
        socialstatus
        intriguestatus

    Shows:
        - All participants and their social capital
        - Current turn order
        - Encounter type and stakes
    """

    key = "socialstatus"
    aliases = ["intriguestatus"]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        location = caller.location

        # Find active encounter
        encounter = SocialEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if not encounter:
            caller.msg("There is no active social encounter here.")
            return

        # Build status display
        lines = [
            f"|y{'=' * 70}|n",
            f"|w{encounter.name}|n",
            f"Type: {encounter.get_encounter_type_display()}",
            f"Round: {encounter.current_round}",
            f"|y{'=' * 70}|n",
            ""
        ]

        # Show stakes if any
        if encounter.stakes:
            lines.append("|yStakes:|n")
            if 'description' in encounter.stakes:
                lines.append(f"  {encounter.stakes['description']}")
            if 'gold' in encounter.stakes:
                lines.append(f"  {encounter.stakes['gold']} crowns")
            lines.append("")

        # Show participants
        lines.append("|wParticipants:|n")
        participants = encounter.participants.all().order_by('initiative_order')
        current_participant = encounter.get_current_participant()

        for p in participants:
            capital_bar = self._make_capital_bar(p.current_social_capital, p.max_social_capital)
            current_marker = " |y<-- Current Turn|n" if p == current_participant else ""

            status = "Active" if p.is_active else "|rDefeated|n"

            lines.append(
                f"  {p.initiative_order + 1}. |c{p.character.name}|n "
                f"({status}) - Stance: {p.stance}"
            )
            lines.append(f"     Capital: {capital_bar}{current_marker}")

        caller.msg("\n".join(lines))

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
