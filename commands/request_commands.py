"""
Unified Request System Commands for Witcher RPG

Handles all types of GM approval requests:
- Character generation
- Special item requests
- Plot hook requests
- Custom requests
"""

from evennia import Command
from django.utils import timezone
from world.witcher_rpg.request_models import (
    UnifiedRequest,
    CharacterGenerationRequest
)
from world.witcher_rpg.models import WitcherCharacter, Vocation, Country


class CmdRequestChar(Command):
    """
    Submit a character generation request for GM approval.

    Usage:
      requestchar

    Starts an interactive character generation process where you'll
    specify your character's vocation, stats, skills, and background.

    The GM will review your request and approve or deny it based on:
    - Mechanical validity (stat/skill point allocation)
    - Background and concept quality
    - Balance considerations
    - Campaign fit

    Note: This is for brand new character creation. To advance an
    existing character's stats/skills to levels 6-7, use the 'request'
    command instead.
    """

    key = "requestchar"
    aliases = ["charrequest", "newchar"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller

        # Check if already has a character
        if WitcherCharacter.objects.filter(character=caller).exists():
            caller.msg("|yYou already have a character!|n")
            caller.msg("To create a new character, please contact a GM.")
            return

        # Check for pending request
        pending = UnifiedRequest.objects.filter(
            requestor=caller,
            request_type='chargen',
            status='pending'
        ).exists()

        if pending:
            caller.msg("|yYou already have a pending character generation request.|n")
            caller.msg("Use |wgmrequests|n to check the status.")
            return

        caller.msg(
            "=" * 70 + "\n"
            "Character Generation Request\n" +
            "=" * 70 + "\n\n"
            "This will create a request for GM approval.\n\n"
            "|rNOTE:|n Full interactive character generation not yet implemented.\n"
            "For now, please contact a GM directly to create your character.\n\n"
            "The character generation system will include:\n"
            "  - Choose vocation (Witcher, Soldier, Merchant, Artisan, etc.)\n"
            "  - Allocate 24 stat points\n"
            "  - Allocate 25 skill points\n"
            "  - Choose country of origin\n"
            "  - Select social rank\n"
            "  - Write character background\n\n"
            "Once submitted, a GM will review and approve/deny your request.\n" +
            "=" * 70
        )


class CmdGMRequests(Command):
    """
    View all pending GM approval requests (GM only).

    Usage:
      gmrequests
      gmrequests [pending|approved|denied|all]
      gmrequests chargen
      gmrequests advancement

    Shows all requests by status or type. Without arguments, shows
    only pending requests.

    Filters:
      pending    - Only pending requests (default)
      approved   - Only approved requests
      denied     - Only denied requests
      all        - All requests regardless of status

    Request types:
      chargen             - Character generation
      advancement_stat    - Stat advancement (6-7)
      advancement_skill   - Skill advancement (6-7)
      special_item        - Special item request
      plot_hook           - Plot hook request
      custom              - Custom request

    Use |wapprovereq <id>|n to approve a request
    Use |wdenyreq <id> <reason>|n to deny a request
    """

    key = "gmrequests"
    aliases = ["requests", "approvalrequests"]
    locks = "cmd:perm(Builder)"
    help_category = "GM"

    def func(self):
        # Parse filter
        filter_status = 'pending'
        filter_type = None

        if self.args:
            arg = self.args.strip().lower()
            if arg in ['pending', 'approved', 'denied', 'all']:
                filter_status = arg
            elif arg in ['chargen', 'advancement_stat', 'advancement_skill',
                        'special_item', 'plot_hook', 'custom', 'advancement']:
                filter_type = arg
                filter_status = 'all'

        # Get requests
        requests = UnifiedRequest.objects.select_related(
            'requestor', 'reviewed_by'
        ).order_by('-created_at')

        # Apply filters
        if filter_status != 'all':
            requests = requests.filter(status=filter_status)

        if filter_type:
            if filter_type == 'advancement':
                requests = requests.filter(
                    request_type__in=['advancement_stat', 'advancement_skill']
                )
            else:
                requests = requests.filter(request_type=filter_type)

        if not requests.exists():
            if filter_status == 'pending':
                self.caller.msg("No pending requests.")
            else:
                self.caller.msg(f"No {filter_status} requests found.")
            return

        # Build output
        lines = []
        lines.append("=" * 70)
        if filter_status == 'pending':
            lines.append(f"Pending GM Approval Requests ({requests.count()})")
        else:
            lines.append(f"GM Approval Requests ({requests.count()})")
        lines.append("=" * 70)

        for request in requests:
            # Status indicator
            if request.status == 'approved':
                status = "|g[APPROVED]|n"
            elif request.status == 'denied':
                status = "|r[DENIED]|n"
            elif request.status == 'revoked':
                status = "|y[REVOKED]|n"
            else:
                status = "|y[PENDING]|n"

            # Priority indicator
            if request.priority == 'urgent':
                priority = "|r[URGENT]|n"
            elif request.priority == 'high':
                priority = "|y[HIGH]|n"
            else:
                priority = ""

            lines.append("")
            lines.append(f"|wRequest #{request.id}|n {status} {priority}")
            lines.append(f"Type: {request.get_request_type_display()}")
            lines.append(f"From: {request.requestor.name}")
            lines.append(f"Title: {request.title}")
            lines.append(f"Submitted: {request.created_at.strftime('%Y-%m-%d %H:%M')}")

            # Show description (truncated)
            if request.description:
                desc = request.description[:100]
                if len(request.description) > 100:
                    desc += "..."
                lines.append(f"Description: {desc}")

            # Show review info if reviewed
            if request.reviewed_by:
                lines.append(
                    f"Reviewed by: {request.reviewed_by.name} "
                    f"on {request.reviewed_at.strftime('%Y-%m-%d %H:%M')}"
                )
                if request.review_notes:
                    notes = request.review_notes[:80]
                    if len(request.review_notes) > 80:
                        notes += "..."
                    lines.append(f"Notes: {notes}")

            # Show chargen details if applicable
            if request.request_type == 'chargen':
                try:
                    chargen = request.chargen_details
                    lines.append(
                        f"  Character: {chargen.character_name} "
                        f"({chargen.vocation.get_name_display()}, "
                        f"{chargen.race})"
                    )
                    if chargen.validation_errors:
                        lines.append(f"  |rValidation Errors:|n {len(chargen.validation_errors)}")
                except:
                    pass

        lines.append("")
        lines.append("=" * 70)
        lines.append("Commands:")
        lines.append("  |wapprovereq <id> [notes]|n - Approve request")
        lines.append("  |wdenyreq <id> <reason>|n - Deny request")
        lines.append("  |wviewreq <id>|n - View full request details")
        lines.append("=" * 70)

        self.caller.msg("\n".join(lines))


class CmdApproveRequest(Command):
    """
    Approve a GM approval request (GM only).

    Usage:
      approvereq <request_id> [notes]
      approvereq 42 Great character concept!
      approvereq 15

    Approves a pending request. Depending on the request type:
    - chargen: Creates the character
    - advancement: Applies the stat/skill increase
    - special_item: Notifies player of approval
    - plot_hook: Notifies player of approval

    Optional notes will be shown to the player.
    """

    key = "approvereq"
    aliases = ["approve", "acceptreq"]
    locks = "cmd:perm(Builder)"
    help_category = "GM"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: approvereq <request_id> [notes]")
            return

        # Parse ID and notes
        parts = self.args.strip().split(None, 1)
        request_id = parts[0]
        notes = parts[1] if len(parts) > 1 else ""

        # Get request
        try:
            request = UnifiedRequest.objects.select_related(
                'requestor'
            ).get(id=request_id)
        except UnifiedRequest.DoesNotExist:
            self.caller.msg(f"Request #{request_id} not found.")
            return
        except ValueError:
            self.caller.msg("Request ID must be a number.")
            return

        # Check if already reviewed
        if request.status != 'pending':
            self.caller.msg(
                f"Request #{request_id} has already been {request.status}."
            )
            return

        # Approve request
        request.approve(self.caller, notes)

        # Handle based on type
        if request.request_type == 'chargen':
            self._handle_chargen_approval(request)
        elif request.request_type in ['advancement_stat', 'advancement_skill']:
            self._handle_advancement_approval(request)
        else:
            # Generic approval
            self._handle_generic_approval(request)

        # Notify GM
        self.caller.msg(
            f"|gRequest #{request.id} approved!|n\n"
            f"Type: {request.get_request_type_display()}\n"
            f"From: {request.requestor.name}\n"
            f"Title: {request.title}"
        )

    def _handle_chargen_approval(self, request):
        """Handle character generation approval."""
        try:
            chargen = request.chargen_details

            # TODO: Actually create the character
            # For now, just notify
            request.requestor.msg(
                "=" * 70 + "\n"
                "|g=== Character Generation Request APPROVED ===|n\n" +
                "=" * 70 + "\n"
                f"Character: {chargen.character_name}\n"
                f"Vocation: {chargen.vocation.get_name_display()}\n"
                f"Approved by: {request.reviewed_by.name}\n\n"
                f"{request.review_notes}\n\n"
                "Your character will be created shortly.\n" +
                "=" * 70
            )

        except Exception as e:
            self.caller.msg(f"|rError processing chargen approval:|n {e}")

    def _handle_advancement_approval(self, request):
        """Handle advancement request approval."""
        # This integrates with the existing advancement system
        # The ApprovalRequest model should handle the actual stat/skill increase

        request.requestor.msg(
            "=" * 70 + "\n"
            "|g=== Advancement Request APPROVED ===|n\n" +
            "=" * 70 + "\n"
            f"Request: {request.title}\n"
            f"Approved by: {request.reviewed_by.name}\n\n"
            f"{request.review_notes}\n\n"
            "Your character has been advanced!\n" +
            "=" * 70
        )

    def _handle_generic_approval(self, request):
        """Handle generic request approval."""
        request.requestor.msg(
            "=" * 70 + "\n"
            "|g=== Request APPROVED ===|n\n" +
            "=" * 70 + "\n"
            f"Type: {request.get_request_type_display()}\n"
            f"Title: {request.title}\n"
            f"Approved by: {request.reviewed_by.name}\n\n"
            f"{request.review_notes}\n" +
            "=" * 70
        )


class CmdDenyRequest(Command):
    """
    Deny a GM approval request (GM only).

    Usage:
      denyreq <request_id> <reason>
      denyreq 42 Need more background detail and in-game justification

    Denies a pending request with a reason that will be shown to the player.
    The reason should explain what needs improvement or why it was denied.
    """

    key = "denyreq"
    aliases = ["deny", "rejectreq"]
    locks = "cmd:perm(Builder)"
    help_category = "GM"

    def func(self):
        if not self.args or " " not in self.args:
            self.caller.msg("Usage: denyreq <request_id> <reason>")
            self.caller.msg("A reason is required.")
            return

        # Parse ID and reason
        parts = self.args.strip().split(None, 1)
        request_id = parts[0]
        reason = parts[1]

        # Get request
        try:
            request = UnifiedRequest.objects.select_related(
                'requestor'
            ).get(id=request_id)
        except UnifiedRequest.DoesNotExist:
            self.caller.msg(f"Request #{request_id} not found.")
            return
        except ValueError:
            self.caller.msg("Request ID must be a number.")
            return

        # Check if already reviewed
        if request.status != 'pending':
            self.caller.msg(
                f"Request #{request_id} has already been {request.status}."
            )
            return

        # Deny request
        request.deny(self.caller, reason)

        # Notify player
        request.requestor.msg(
            "=" * 70 + "\n"
            "|r=== Request DENIED ===|n\n" +
            "=" * 70 + "\n"
            f"Type: {request.get_request_type_display()}\n"
            f"Title: {request.title}\n"
            f"Reviewed by: {request.reviewed_by.name}\n\n"
            f"|wReason:|n\n{reason}\n\n"
            "You may submit a new request addressing these concerns.\n" +
            "=" * 70
        )

        # Notify GM
        self.caller.msg(
            f"|rRequest #{request.id} denied.|n\n"
            f"Type: {request.get_request_type_display()}\n"
            f"From: {request.requestor.name}\n"
            f"Title: {request.title}\n\n"
            f"Player has been notified."
        )


class CmdViewRequest(Command):
    """
    View detailed information about a specific request.

    Usage:
      viewreq <request_id>
      viewreq 42

    Shows complete details about a request including:
    - Full description
    - Request data (stats, skills, etc.)
    - Validation results (for chargen)
    - Full review notes
    - History/timeline
    """

    key = "viewreq"
    aliases = ["showreq", "requestinfo"]
    locks = "cmd:perm(Builder)"
    help_category = "GM"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: viewreq <request_id>")
            return

        request_id = self.args.strip()

        # Get request
        try:
            request = UnifiedRequest.objects.select_related(
                'requestor', 'reviewed_by'
            ).get(id=request_id)
        except UnifiedRequest.DoesNotExist:
            self.caller.msg(f"Request #{request_id} not found.")
            return
        except ValueError:
            self.caller.msg("Request ID must be a number.")
            return

        # Build output
        lines = []
        lines.append("=" * 70)
        lines.append(f"Request #{request.id} - {request.get_request_type_display()}")
        lines.append("=" * 70)

        # Status
        if request.status == 'approved':
            status = "|g[APPROVED]|n"
        elif request.status == 'denied':
            status = "|r[DENIED]|n"
        elif request.status == 'revoked':
            status = "|y[REVOKED]|n"
        else:
            status = "|y[PENDING]|n"

        lines.append(f"Status: {status}")
        lines.append(f"Priority: {request.get_priority_display()}")
        lines.append(f"Requestor: {request.requestor.name}")
        lines.append(f"Created: {request.created_at.strftime('%Y-%m-%d %H:%M')}")

        if request.reviewed_by:
            lines.append(
                f"Reviewed by: {request.reviewed_by.name} "
                f"on {request.reviewed_at.strftime('%Y-%m-%d %H:%M')}"
            )

        lines.append("")
        lines.append("|wTitle:|n")
        lines.append(request.title)
        lines.append("")
        lines.append("|wDescription:|n")
        lines.append(request.description)

        # Show request data
        if request.request_data:
            lines.append("")
            lines.append("|wRequest Data:|n")
            for key, value in request.request_data.items():
                lines.append(f"  {key}: {value}")

        # Show chargen details
        if request.request_type == 'chargen':
            try:
                chargen = request.chargen_details
                lines.append("")
                lines.append("|wCharacter Generation Details:|n")
                lines.append(f"  Name: {chargen.character_name}")
                lines.append(f"  Vocation: {chargen.vocation.get_name_display()}")
                lines.append(f"  Race: {chargen.race}")
                if chargen.country:
                    lines.append(f"  Country: {chargen.country.get_name_display()}")
                lines.append(f"  Social Rank: {chargen.get_social_rank_display()}")
                lines.append("")
                lines.append("|wStat Allocation:|n")
                for stat, value in chargen.stats_allocation.items():
                    lines.append(f"  {stat}: {value}")
                lines.append("")
                lines.append("|wSkill Allocation:|n")
                for skill, value in chargen.skills_allocation.items():
                    lines.append(f"  {skill}: {value}")
                lines.append("")
                lines.append("|wBackground:|n")
                lines.append(chargen.background)
                lines.append("")
                lines.append(f"Stats Valid: {'|gYes|n' if chargen.stats_valid else '|rNo|n'}")
                lines.append(f"Skills Valid: {'|gYes|n' if chargen.skills_valid else '|rNo|n'}")
                if chargen.validation_errors:
                    lines.append("|rValidation Errors:|n")
                    for error in chargen.validation_errors:
                        lines.append(f"  - {error}")
            except Exception as e:
                lines.append(f"|rError loading chargen details:|n {e}")

        # Show review notes
        if request.review_notes:
            lines.append("")
            lines.append("|wReview Notes:|n")
            lines.append(request.review_notes)

        lines.append("")
        lines.append("=" * 70)

        if request.status == 'pending':
            lines.append("Commands:")
            lines.append(f"  |wapprovereq {request.id} [notes]|n - Approve this request")
            lines.append(f"  |wdenyreq {request.id} <reason>|n - Deny this request")
            lines.append("=" * 70)

        self.caller.msg("\n".join(lines))


class CmdMyRequests(Command):
    """
    View your submitted requests.

    Usage:
      myrequests
      myrequests [pending|approved|denied|all]

    Shows all requests you've submitted with their current status.
    Use this to check on pending approvals or review past requests.
    """

    key = "myrequests"
    aliases = ["myreqs"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller

        # Parse filter
        filter_status = 'all'
        if self.args:
            arg = self.args.strip().lower()
            if arg in ['pending', 'approved', 'denied', 'all']:
                filter_status = arg

        # Get requests
        requests = UnifiedRequest.objects.filter(
            requestor=caller
        ).select_related('reviewed_by').order_by('-created_at')

        # Apply filter
        if filter_status != 'all':
            requests = requests.filter(status=filter_status)

        if not requests.exists():
            caller.msg("You haven't submitted any requests yet.")
            return

        # Build output
        lines = []
        lines.append("=" * 70)
        lines.append(f"Your Submitted Requests ({requests.count()})")
        lines.append("=" * 70)

        for request in requests:
            # Status indicator
            if request.status == 'approved':
                status = "|g[APPROVED]|n"
            elif request.status == 'denied':
                status = "|r[DENIED]|n"
            elif request.status == 'revoked':
                status = "|y[REVOKED]|n"
            else:
                status = "|y[PENDING]|n"

            lines.append("")
            lines.append(f"|wRequest #{request.id}|n {status}")
            lines.append(f"Type: {request.get_request_type_display()}")
            lines.append(f"Title: {request.title}")
            lines.append(f"Submitted: {request.created_at.strftime('%Y-%m-%d %H:%M')}")

            if request.reviewed_by:
                lines.append(
                    f"Reviewed by: {request.reviewed_by.name} "
                    f"on {request.reviewed_at.strftime('%Y-%m-%d %H:%M')}"
                )
                if request.review_notes:
                    lines.append(f"Notes: {request.review_notes}")

        lines.append("")
        lines.append("=" * 70)

        caller.msg("\n".join(lines))
