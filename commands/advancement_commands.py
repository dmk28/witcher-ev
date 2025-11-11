"""
Character Advancement Commands for Witcher RPG

Commands for spending XP to improve stats and skills.
"""

from evennia import Command
from world.witcher_rpg.advancement_system import AdvancementManager, AdvancementCalculator
from world.witcher_rpg.advancement_models import ApprovalRequest, AdvancementLog


class CmdAdvance(Command):
    """
    Spend XP to advance stats or skills.

    Usage:
        advance
        advance <stat/skill>
        advance strength
        advance blades

    Cost Formula:
        Stats (1-5): New Rating × 10 XP
        Stats (6-7): New Rating × 20 XP (requires GM approval)
        Skills (1-5): New Rating × 5 XP
        Skills (6-7): New Rating × 15 XP (requires GM approval)

    Examples:
        Strength 3 → 4: 40 XP
        Strength 5 → 6: 120 XP (GM approval required)
        Blades 4 → 5: 25 XP
        Blades 6 → 7: 105 XP (GM approval required)

    With no arguments, shows all possible advancements and their costs.

    For levels 6-7, use 'request <stat/skill> <justification>' to submit
    for GM approval.
    """

    key = "advance"
    aliases = ["train", "improve"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller

        if not caller.db_character:
            caller.msg("You don't have character data.")
            return

        if not self.args:
            # Show advancement preview
            self._show_advancement_options()
            return

        stat_or_skill = self.args.strip().lower()

        # Check if it's a stat
        if stat_or_skill in AdvancementManager.STAT_NAMES:
            result = AdvancementManager.advance_stat(caller, stat_or_skill)
        # Check if it's a skill
        elif stat_or_skill in AdvancementManager.SKILL_NAMES:
            result = AdvancementManager.advance_skill(caller, stat_or_skill)
        else:
            caller.msg(f"Unknown stat or skill: {stat_or_skill}")
            return

        if result['success']:
            caller.msg(
                f"|gAdvancement successful!|n\n"
                f"{result.get('stat') or result.get('skill')} "
                f"{result['old_value']} → |w{result['new_value']}|n\n"
                f"XP spent: {result['xp_cost']}\n"
                f"Remaining XP: {result['remaining_xp']}"
            )

            if result.get('approved_by'):
                caller.msg(f"|yApproved by GM: {result['approved_by']}|n")

        elif result.get('needs_approval'):
            caller.msg(
                f"|yGM approval required|n for {stat_or_skill.title()} level {result['target_value']}.\n"
                f"Cost: {result['xp_cost']} XP\n\n"
                f"Use: |wrequest {stat_or_skill} <justification>|n"
            )
        else:
            caller.msg(f"|r{result['message']}|n")

    def _show_advancement_options(self):
        """Show all possible advancements with costs."""
        preview = AdvancementManager.get_advancement_cost_preview(self.caller)

        if not preview:
            self.caller.msg("No character data available.")
            return

        lines = []
        lines.append(f"|y{'=' * 70}|n")
        lines.append(f"|wCharacter Advancement Options|n")
        lines.append(f"Available XP: |c{preview['xp_available']}|n")
        lines.append(f"|y{'=' * 70}|n")

        # Stats
        lines.append("\n|wStats:|n (1-5: NR×10 XP | 6-7: NR×20 XP + GM approval)")
        for stat_name, data in sorted(preview['stats'].items()):
            if data['current'] >= 7:
                continue  # Skip maxed stats

            approval_marker = " |y*|n" if data['needs_approval'] else ""
            affordable = "|g✓|n" if data['can_afford'] else "|r✗|n"

            lines.append(
                f"  {affordable} {stat_name.title():<15} "
                f"{data['current']} → {data['next']}  "
                f"|c{data['cost']} XP|n{approval_marker}"
            )

        # Skills
        lines.append("\n|wSkills:|n (1-5: NR×5 XP | 6-7: NR×15 XP + GM approval)")
        for skill_name, data in sorted(preview['skills'].items()):
            if data['current'] >= 10:
                continue  # Skip maxed skills

            if data['current'] == 0:
                continue  # Skip unused skills for brevity

            approval_marker = " |y*|n" if data['needs_approval'] else ""
            affordable = "|g✓|n" if data['can_afford'] else "|r✗|n"

            lines.append(
                f"  {affordable} {skill_name.title():<15} "
                f"{data['current']} → {data['next']}  "
                f"|c{data['cost']} XP|n{approval_marker}"
            )

        lines.append(f"\n|y*|n = Requires GM approval")
        lines.append(f"\n|yUsage:|n advance <stat/skill>")

        self.caller.msg("\n".join(lines))


class CmdRequest(Command):
    """
    Request GM approval for high-level advancement (6-7).

    Usage:
        request <stat/skill> <justification>
        request strength My character has been training with master warriors
        request blades Defeated multiple legendary swordsmen in combat

    GM approval is required for advancing stats or skills to level 6 or 7.
    Provide a justification explaining why your character deserves this
    exceptional advancement.

    GMs will review your request and approve or deny it.
    """

    key = "request"
    aliases = ["requestadvance"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller

        if not caller.db_character:
            caller.msg("You don't have character data.")
            return

        if not self.args:
            caller.msg("Usage: request <stat/skill> <justification>")
            return

        args_list = self.args.strip().split(None, 1)
        if len(args_list) < 2:
            caller.msg("Please provide a justification for this advancement.")
            return

        stat_or_skill = args_list[0].lower()
        justification = args_list[1]

        # Determine type
        if stat_or_skill in AdvancementManager.STAT_NAMES:
            advancement_type = 'stat'
        elif stat_or_skill in AdvancementManager.SKILL_NAMES:
            advancement_type = 'skill'
        else:
            caller.msg(f"Unknown stat or skill: {stat_or_skill}")
            return

        # Create request
        result = AdvancementManager.create_approval_request(
            caller, advancement_type, stat_or_skill, justification
        )

        if result['success']:
            caller.msg(
                f"|gRequest submitted!|n\n"
                f"{stat_or_skill.title()}: {result['current_value']} → {result['target_value']}\n"
                f"Cost: {result['xp_cost']} XP\n"
                f"Request ID: {result['request_id']}\n\n"
                f"A GM will review your request."
            )
        else:
            caller.msg(f"|r{result['message']}|n")


class CmdApprove(Command):
    """
    Approve or deny advancement requests (GM only).

    Usage:
        approve
        approve <request_id>
        approve <request_id> <notes>
        deny <request_id> <reason>

    With no arguments, shows all pending approval requests.

    With a request ID, approves the request (immediately applies advancement
    and deducts XP from the character).

    GMs can add notes explaining their decision.

    Examples:
        approve
        approve 5
        approve 5 Excellent roleplay justification
        deny 3 Need more in-game training first
    """

    key = "approve"
    aliases = ["deny", "approvals"]
    locks = "perm(Builder)"  # Restrict to staff
    help_category = "GM"

    def func(self):
        caller = self.caller

        if not self.args:
            # Show pending requests
            self._show_pending_requests()
            return

        args_list = self.args.strip().split(None, 1)
        try:
            request_id = int(args_list[0])
        except ValueError:
            caller.msg("Request ID must be a number.")
            return

        notes = args_list[1] if len(args_list) > 1 else ""

        # Determine if approving or denying
        approve = self.cmdname.lower() != "deny"

        # Process request
        result = AdvancementManager.process_approval(
            request_id, caller, approve, notes
        )

        if result['success']:
            if result['approved']:
                caller.msg(
                    f"|gRequest approved!|n\n"
                    f"Character: {result['character']}\n"
                    f"Advancement: {result['advancement']}\n"
                    f"XP deducted: {result['xp_cost']}"
                )

                # Notify player
                character = ApprovalRequest.objects.get(id=request_id).character
                if character.has_account:
                    character.msg(
                        f"|g=== Advancement Approved ===|n\n"
                        f"Your request for {result['advancement']} has been approved by {caller.name}!\n"
                        f"XP spent: {result['xp_cost']}\n"
                        f"{notes if notes else ''}"
                    )
            else:
                caller.msg(
                    f"|yRequest denied.|n\n"
                    f"Character: {result['character']}\n"
                    f"Advancement: {result['advancement']}"
                )

                # Notify player
                character = ApprovalRequest.objects.get(id=request_id).character
                if character.has_account:
                    character.msg(
                        f"|y=== Advancement Request Denied ===|n\n"
                        f"Your request for {result['advancement']} was denied by {caller.name}.\n"
                        f"Reason: {notes if notes else 'No reason given'}"
                    )
        else:
            caller.msg(f"|r{result['message']}|n")

    def _show_pending_requests(self):
        """Show all pending advancement approval requests."""
        requests = ApprovalRequest.objects.filter(status='pending').order_by('created_at')

        if not requests.exists():
            self.caller.msg("No pending advancement approval requests.")
            return

        lines = []
        lines.append(f"|y{'=' * 70}|n")
        lines.append(f"|wPending Advancement Approval Requests|n")
        lines.append(f"|y{'=' * 70}|n")

        for req in requests:
            lines.append(f"\n|cRequest ID: {req.id}|n")
            lines.append(f"Character: |w{req.character.name}|n")
            lines.append(
                f"Advancement: {req.stat_or_skill_name.title()} "
                f"{req.current_value} → {req.target_value}"
            )
            lines.append(f"XP Cost: {req.xp_cost}")
            lines.append(f"Type: {req.get_advancement_type_display()}")
            lines.append(f"Submitted: {req.created_at.strftime('%Y-%m-%d %H:%M')}")

            if req.justification:
                lines.append(f"Justification: |y{req.justification}|n")

        lines.append(f"\n|yCommands:|n")
        lines.append(f"approve <id> [notes] - Approve request")
        lines.append(f"deny <id> <reason> - Deny request")

        self.caller.msg("\n".join(lines))


class CmdAdvancementHistory(Command):
    """
    View your character's advancement history.

    Usage:
        history
        history <character>

    Shows all stat and skill improvements, XP costs, and GM approvals.
    GMs can view other characters' history by specifying the character name.
    """

    key = "history"
    aliases = ["advancementhistory", "advancements"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller

        # Determine target character
        if self.args and caller.check_permstring("perm(Builder)"):
            # GM viewing another character
            target = caller.search(self.args.strip())
            if not target:
                return
        else:
            target = caller

        if not target.db_character:
            caller.msg(f"{target.name} doesn't have character data.")
            return

        # Get advancement log
        log = AdvancementLog.objects.filter(character=target).order_by('-timestamp')[:20]

        if not log.exists():
            caller.msg(f"{target.name} has no advancement history.")
            return

        lines = []
        lines.append(f"|y{'=' * 70}|n")
        lines.append(f"|wAdvancement History: {target.name}|n")
        lines.append(f"|y{'=' * 70}|n")

        for entry in log:
            approval_note = ""
            if entry.required_approval:
                approval_note = f" |y(GM: {entry.approved_by.name if entry.approved_by else 'Unknown'})|n"

            type_label = "Stat" if entry.advancement_type == 'stat' else "Skill"

            lines.append(
                f"{entry.timestamp.strftime('%Y-%m-%d')} | "
                f"{type_label}: |w{entry.stat_or_skill_name.title()}|n "
                f"{entry.old_value} → {entry.new_value} "
                f"(-{entry.xp_cost} XP){approval_note}"
            )

        # Show current XP
        lines.append(f"\n|wCurrent XP:|n {target.db_character.experience_points}")

        caller.msg("\n".join(lines))
