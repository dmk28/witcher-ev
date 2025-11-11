"""
Organization and Income commands for Witcher RPG.

Commands for collecting passive income, joining organizations, and managing memberships.
"""

from evennia import Command
from world.witcher_rpg.organization_models import (
    Organization,
    OrganizationMembership,
    OrganizationType,
    IncomeLog
)
from world.witcher_rpg.models import WitcherCharacter
from world.witcher_rpg.mush_utils import convert_mush_tokens
from django.utils import timezone


class CmdIncome(Command):
    """
    Collect monthly income from your organizations.

    Usage:
      +income

    Collects passive income from all organizations you're a member of.
    Income can be collected once every 30 days per organization.
    """

    key = "+income"
    aliases = ["income", "collect"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller

        # Get character
        try:
            character = WitcherCharacter.objects.get(db_object=caller)
        except WitcherCharacter.DoesNotExist:
            caller.msg("|rYour character data could not be found.|n")
            return

        # Get all active memberships
        memberships = OrganizationMembership.objects.filter(
            member=caller,
            is_active=True
        )

        if not memberships.exists():
            caller.msg("|yYou are not a member of any organizations.|n")
            caller.msg("Use |w+organizations|n to see available organizations.")
            return

        # Try to collect from each membership
        lines = []
        lines.append("%r")
        lines.append("=" * 70)
        lines.append("Monthly Income Collection")
        lines.append("=" * 70)
        lines.append("%r")

        total_collected = 0
        collected_count = 0

        for membership in memberships:
            success, amount, message = membership.collect_income()

            if success:
                # Add gold to character
                character.gold += amount
                character.save()

                # Log the income
                IncomeLog.objects.create(
                    character=caller,
                    organization=membership.organization,
                    amount=amount,
                    source=f"Rank {membership.organization_rank} Stipend"
                )

                total_collected += amount
                collected_count += 1

                lines.append(f"|g✓|n {membership.organization.name}")
                lines.append(f"%t%tRank: {membership.organization_rank}")
                if membership.role:
                    lines.append(f"%t%tRole: {membership.role}")
                lines.append(f"%t%tIncome: |y{amount:,} crowns|n")
            else:
                lines.append(f"|r✗|n {membership.organization.name}")
                lines.append(f"%t%t{message}")

            lines.append("%r")

        lines.append("-" * 70)
        if collected_count > 0:
            lines.append(f"|gTotal Collected:|n |y{total_collected:,} crowns|n")
            lines.append(f"|gNew Balance:|n |y{character.gold:,} crowns|n")
        else:
            lines.append("|yNo income collected this time.|n")
        lines.append("=" * 70)
        lines.append("%r")

        caller.msg(convert_mush_tokens("%r".join(lines)))


class CmdOrganizations(Command):
    """
    View available organizations or details about a specific organization.

    Usage:
      +organizations
      +organizations <name>
      +organizations/all          - Show all organizations (including inactive)
      +organizations/type <type>  - Filter by organization type

    Organization types:
      noble_house, witcher_school, trading_company, military_order,
      magical_academy, criminal_syndicate, guild, religious_order
    """

    key = "+organizations"
    aliases = ["orgs", "+orgs"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller

        # View specific organization
        if self.args and not self.switches:
            org_name = self.args.strip()
            try:
                org = Organization.objects.get(name__iexact=org_name)
            except Organization.DoesNotExist:
                caller.msg(f"|rOrganization '{org_name}' not found.|n")
                return

            self._view_organization(org)
            return

        # Filter by type
        if "type" in self.switches:
            if not self.args:
                caller.msg("|rYou must specify an organization type.|n")
                return
            org_type = self.args.strip().lower()
            orgs = Organization.objects.filter(
                organization_type=org_type,
                is_active=True
            )
        elif "all" in self.switches:
            orgs = Organization.objects.all()
        else:
            orgs = Organization.objects.filter(is_active=True)

        if not orgs.exists():
            caller.msg("|yNo organizations found.|n")
            return

        # List organizations
        lines = []
        lines.append("%r")
        lines.append("=" * 80)
        lines.append("Available Organizations")
        lines.append("=" * 80)
        lines.append("%r")
        lines.append(f"{'Name':<30} {'Type':<25} {'Members':<10} {'Leader':<15}")
        lines.append("-" * 80)

        for org in orgs:
            org_type = org.get_organization_type_display()
            member_count = org.get_member_count()
            leader_name = org.leader.db_key if org.leader else "None"

            status_marker = "" if org.is_active else " |r(Inactive)|n"

            lines.append(
                f"{org.name:<30} {org_type:<25} {member_count:<10} {leader_name:<15}{status_marker}"
            )

        lines.append("=" * 80)
        lines.append("%r")
        lines.append("Use |w+organizations <name>|n to view details about an organization.")
        lines.append("Use |w+orgjoin <name>|n to request membership.")
        lines.append("%r")

        caller.msg(convert_mush_tokens("%r".join(lines)))

    def _view_organization(self, org):
        """Display detailed information about an organization."""
        caller = self.caller

        lines = []
        lines.append("%r")
        lines.append("=" * 70)
        lines.append(f"{org.name}")
        lines.append("=" * 70)
        lines.append("%r")

        # Basic info
        lines.append(f"|wType:|n {org.get_organization_type_display()}")
        lines.append(f"|wLeader:|n {org.leader.db_key if org.leader else 'None'}")
        lines.append(f"|wActive:|n {'Yes' if org.is_active else '|rNo|n'}")
        lines.append(f"|wRequires Approval:|n {'Yes' if org.requires_approval else 'No'}")
        lines.append("%r")

        # Description
        lines.append("|wDescription:|n")
        lines.append(org.description)
        lines.append("%r")

        # Income information
        lines.append("|wIncome Information:|n")
        lines.append(f"%t%tBase Income Multiplier: {org.base_income_multiplier}x")
        if org.member_tithe_percentage > 0:
            lines.append(f"%t%tMember Tithing: {org.member_tithe_percentage}%")
            lines.append(f"%t%tLeader Share: {org.leader_share_percentage}%")
        if org.organization_type == OrganizationType.TRADING_COMPANY:
            lines.append(f"%t%tInvestment Level: {org.investment_level}")
            lines.append(f"%t%tInvestment Return: 5% monthly")
        lines.append("%r")

        # Rank income table
        lines.append("|wMonthly Income by Rank:|n")
        rank_income = {
            1: 100, 2: 300, 3: 800, 4: 2000, 5: 5000
        }
        for rank, base in rank_income.items():
            modified = int(base * org.base_income_multiplier)
            lines.append(f"%t%tRank {rank}: {modified:,} crowns/month")
        lines.append("%r")

        # Members
        memberships = OrganizationMembership.objects.filter(
            organization=org,
            is_active=True
        ).order_by('-organization_rank', 'joined_date')

        lines.append(f"|wMembers:|n ({memberships.count()})")
        if memberships.exists():
            lines.append(f"%t%t{'Name':<20} {'Rank':<8} {'Role':<20}")
            lines.append("%t%t" + "-" * 48)
            for membership in memberships[:10]:  # Show first 10
                member_name = membership.member.db_key
                rank = f"Rank {membership.organization_rank}"
                role = membership.role or "-"
                lines.append(f"%t%t{member_name:<20} {rank:<8} {role:<20}")
            if memberships.count() > 10:
                lines.append(f"%t%t... and {memberships.count() - 10} more")
        else:
            lines.append("%t%tNone")

        lines.append("%r")
        lines.append("=" * 70)
        lines.append("%r")

        # Check if caller is a member
        try:
            membership = OrganizationMembership.objects.get(
                organization=org,
                member=caller,
                is_active=True
            )
            lines.append(f"|gYou are a member of this organization (Rank {membership.organization_rank}).|n")
        except OrganizationMembership.DoesNotExist:
            if org.is_active:
                lines.append("Use |w+orgjoin " + org.name + "|n to request membership.")

        lines.append("%r")
        caller.msg(convert_mush_tokens("%r".join(lines)))


class CmdOrgJoin(Command):
    """
    Request to join an organization.

    Usage:
      +orgjoin <organization name>

    Submits a membership request to the organization's leadership.
    Some organizations require approval, others allow immediate joining.
    """

    key = "+orgjoin"
    aliases = ["orgjoin"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +orgjoin <organization name>")
            return

        org_name = self.args.strip()

        # Find organization
        try:
            org = Organization.objects.get(name__iexact=org_name, is_active=True)
        except Organization.DoesNotExist:
            caller.msg(f"|rOrganization '{org_name}' not found.|n")
            return

        # Check if already a member
        existing = OrganizationMembership.objects.filter(
            organization=org,
            member=caller,
            is_active=True
        ).first()

        if existing:
            caller.msg(f"|yYou are already a member of {org.name}.|n")
            return

        # Create membership
        membership = OrganizationMembership.objects.create(
            organization=org,
            member=caller,
            organization_rank=1,
            is_active=True,
            is_approved=not org.requires_approval
        )

        if org.requires_approval:
            caller.msg(f"|gMembership request submitted to {org.name}.|n")
            caller.msg("Your request requires approval from the organization's leadership.")

            # Notify leader
            if org.leader and hasattr(org.leader, 'msg'):
                org.leader.msg(
                    f"|y[ORGANIZATION]|n {caller.db_key} has requested to join {org.name}."
                )
        else:
            caller.msg(f"|gYou have joined {org.name}!|n")
            caller.msg(f"You will receive |y{membership.calculate_total_income():,} crowns|n per month.")
            caller.msg("Use |w+income|n to collect your monthly stipend.")


class CmdOrgLeave(Command):
    """
    Leave an organization.

    Usage:
      +orgleave <organization name>

    Deactivates your membership in the organization.
    """

    key = "+orgleave"
    aliases = ["orgleave"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +orgleave <organization name>")
            return

        org_name = self.args.strip()

        # Find membership
        try:
            org = Organization.objects.get(name__iexact=org_name)
            membership = OrganizationMembership.objects.get(
                organization=org,
                member=caller,
                is_active=True
            )
        except (Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            caller.msg(f"|rYou are not a member of '{org_name}'.|n")
            return

        # Check if leader
        if org.leader == caller:
            caller.msg("|rYou cannot leave an organization you lead.|n")
            caller.msg("Transfer leadership first using |w+orgmanage|n.")
            return

        # Deactivate membership
        membership.is_active = False
        membership.save()

        caller.msg(f"|gYou have left {org.name}.|n")

        # Notify leader
        if org.leader and hasattr(org.leader, 'msg'):
            org.leader.msg(
                f"|y[ORGANIZATION]|n {caller.db_key} has left {org.name}."
            )


class CmdOrgInvest(Command):
    """
    Invest gold in a trading company (trading companies only).

    Usage:
      +orginvest <organization name> = <amount>

    Invest gold in a trading company to increase your personal investment.
    Trading companies provide 5% monthly return on investment.
    """

    key = "+orginvest"
    aliases = ["orginvest"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller

        if not self.args or '=' not in self.args:
            caller.msg("Usage: +orginvest <organization name> = <amount>")
            return

        org_name, amount_str = self.args.split('=', 1)
        org_name = org_name.strip()
        amount_str = amount_str.strip()

        # Parse amount
        try:
            amount = int(amount_str.replace(',', ''))
        except ValueError:
            caller.msg("|rInvalid amount.|n")
            return

        if amount <= 0:
            caller.msg("|rAmount must be positive.|n")
            return

        # Get character
        try:
            character = WitcherCharacter.objects.get(db_object=caller)
        except WitcherCharacter.DoesNotExist:
            caller.msg("|rYour character data could not be found.|n")
            return

        # Check gold
        if character.gold < amount:
            caller.msg(f"|rInsufficient gold!|n\nYou have: {character.gold:,}\nRequired: {amount:,}")
            return

        # Find membership
        try:
            org = Organization.objects.get(name__iexact=org_name)
            membership = OrganizationMembership.objects.get(
                organization=org,
                member=caller,
                is_active=True,
                is_approved=True
            )
        except (Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            caller.msg(f"|rYou are not an active member of '{org_name}'.|n")
            return

        # Check organization type
        if org.organization_type != OrganizationType.TRADING_COMPANY:
            caller.msg("|rOnly trading companies accept investments.|n")
            return

        # Deduct gold
        character.gold -= amount
        character.save()

        # Add to investment
        membership.personal_investment += amount
        membership.save()

        # Add to organization investment level (every 10,000 gold = 1 level)
        level_increase = amount // 10000
        if level_increase > 0:
            org.investment_level += level_increase
            org.save()

        # Calculate new monthly returns
        monthly_return = membership.calculate_investment_returns()

        caller.msg(f"|gInvested {amount:,} crowns in {org.name}!|n")
        caller.msg(f"Total Investment: {membership.personal_investment:,} crowns")
        caller.msg(f"Monthly Return: {monthly_return:,} crowns (5%)")
        caller.msg(f"New Gold Balance: {character.gold:,} crowns")


class CmdOrgManage(Command):
    """
    Manage your organization (leaders and GMs only).

    Usage:
      +orgmanage <organization>
      +orgmanage <organization>/promote <member> = <rank>
      +orgmanage <organization>/demote <member> = <rank>
      +orgmanage <organization>/setrole <member> = <role>
      +orgmanage <organization>/approve <member>
      +orgmanage <organization>/kick <member>
      +orgmanage <organization>/transfer <member>

    Leaders can manage memberships, ranks, and roles.
    Use /transfer to transfer leadership to another member.
    """

    key = "+orgmanage"
    aliases = ["orgmanage"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +orgmanage <organization>[/switch] [arguments]")
            return

        # Parse org name
        if '/' in self.lhs if self.lhs else '':
            org_name = self.lhs.split('/')[0].strip()
        else:
            org_name = self.args.strip()

        # Find organization
        try:
            org = Organization.objects.get(name__iexact=org_name)
        except Organization.DoesNotExist:
            caller.msg(f"|rOrganization '{org_name}' not found.|n")
            return

        # Check permission (must be leader or GM)
        is_gm = caller.permissions.get("Builder")
        is_leader = org.leader == caller

        if not (is_gm or is_leader):
            caller.msg("|rYou do not have permission to manage this organization.|n")
            return

        # Handle switches
        if "promote" in self.switches or "demote" in self.switches:
            self._change_rank(org, caller)
        elif "setrole" in self.switches:
            self._set_role(org, caller)
        elif "approve" in self.switches:
            self._approve_member(org, caller)
        elif "kick" in self.switches:
            self._kick_member(org, caller)
        elif "transfer" in self.switches:
            self._transfer_leadership(org, caller)
        else:
            self._view_management(org, caller)

    def _view_management(self, org, caller):
        """View organization management panel."""
        lines = []
        lines.append("%r")
        lines.append("=" * 70)
        lines.append(f"Managing: {org.name}")
        lines.append("=" * 70)
        lines.append("%r")

        # Organization stats
        lines.append(f"|wTreasury:|n {org.treasury:,} crowns")
        lines.append(f"|wMembers:|n {org.get_member_count()}")
        if org.organization_type == OrganizationType.TRADING_COMPANY:
            lines.append(f"|wInvestment Level:|n {org.investment_level}")
        lines.append("%r")

        # Pending approvals
        pending = OrganizationMembership.objects.filter(
            organization=org,
            is_active=True,
            is_approved=False
        )
        if pending.exists():
            lines.append("|yPending Approvals:|n")
            for membership in pending:
                lines.append(f"%t%t- {membership.member.db_key}")
            lines.append("%r")

        # Management commands
        lines.append("|wManagement Commands:|n")
        lines.append(f"%t%t+orgmanage {org.name}/promote <member> = <rank>")
        lines.append(f"%t%t+orgmanage {org.name}/demote <member> = <rank>")
        lines.append(f"%t%t+orgmanage {org.name}/setrole <member> = <role>")
        lines.append(f"%t%t+orgmanage {org.name}/approve <member>")
        lines.append(f"%t%t+orgmanage {org.name}/kick <member>")
        lines.append(f"%t%t+orgmanage {org.name}/transfer <member>")

        lines.append("%r")
        lines.append("=" * 70)
        lines.append("%r")
        caller.msg(convert_mush_tokens("%r".join(lines)))

    def _change_rank(self, org, caller):
        """Promote or demote a member."""
        if not self.rhs or '=' not in self.args:
            caller.msg("Usage: +orgmanage <org>/promote <member> = <rank>")
            return

        member_name, rank_str = self.rhs.split('=', 1)
        member_name = member_name.strip()
        rank_str = rank_str.strip()

        try:
            rank = int(rank_str)
        except ValueError:
            caller.msg("|rInvalid rank. Must be 1-5.|n")
            return

        if rank < 1 or rank > 5:
            caller.msg("|rRank must be between 1 and 5.|n")
            return

        # Find member
        try:
            member = caller.search(member_name, global_search=True)
            if not member:
                return
            membership = OrganizationMembership.objects.get(
                organization=org,
                member=member,
                is_active=True
            )
        except OrganizationMembership.DoesNotExist:
            caller.msg(f"|r{member_name} is not a member of {org.name}.|n")
            return

        old_rank = membership.organization_rank
        membership.organization_rank = rank
        membership.save()

        action = "promoted" if rank > old_rank else "demoted" if rank < old_rank else "rank set"
        caller.msg(f"|g{member.db_key} {action} to Rank {rank} in {org.name}.|n")

        # Notify member
        if hasattr(member, 'msg'):
            member.msg(f"|y[ORGANIZATION]|n You have been {action} to Rank {rank} in {org.name}.")

    def _set_role(self, org, caller):
        """Set a member's role/title."""
        if not self.rhs or '=' not in self.args:
            caller.msg("Usage: +orgmanage <org>/setrole <member> = <role>")
            return

        member_name, role = self.rhs.split('=', 1)
        member_name = member_name.strip()
        role = role.strip()

        # Find member
        try:
            member = caller.search(member_name, global_search=True)
            if not member:
                return
            membership = OrganizationMembership.objects.get(
                organization=org,
                member=member,
                is_active=True
            )
        except OrganizationMembership.DoesNotExist:
            caller.msg(f"|r{member_name} is not a member of {org.name}.|n")
            return

        membership.role = role
        membership.save()

        caller.msg(f"|g{member.db_key}'s role set to '{role}' in {org.name}.|n")

        # Notify member
        if hasattr(member, 'msg'):
            member.msg(f"|y[ORGANIZATION]|n Your role in {org.name} is now: {role}")

    def _approve_member(self, org, caller):
        """Approve a pending membership."""
        if not self.rhs:
            caller.msg("Usage: +orgmanage <org>/approve <member>")
            return

        member_name = self.rhs.strip()

        # Find member
        try:
            member = caller.search(member_name, global_search=True)
            if not member:
                return
            membership = OrganizationMembership.objects.get(
                organization=org,
                member=member,
                is_active=True,
                is_approved=False
            )
        except OrganizationMembership.DoesNotExist:
            caller.msg(f"|r{member_name} does not have a pending membership request.|n")
            return

        membership.is_approved = True
        membership.save()

        caller.msg(f"|g{member.db_key}'s membership in {org.name} has been approved.|n")

        # Notify member
        if hasattr(member, 'msg'):
            member.msg(f"|g[ORGANIZATION]|n Your membership in {org.name} has been approved!")
            member.msg("Use |w+income|n to collect your monthly stipend.")

    def _kick_member(self, org, caller):
        """Kick a member from the organization."""
        if not self.rhs:
            caller.msg("Usage: +orgmanage <org>/kick <member>")
            return

        member_name = self.rhs.strip()

        # Find member
        try:
            member = caller.search(member_name, global_search=True)
            if not member:
                return
            membership = OrganizationMembership.objects.get(
                organization=org,
                member=member,
                is_active=True
            )
        except OrganizationMembership.DoesNotExist:
            caller.msg(f"|r{member_name} is not a member of {org.name}.|n")
            return

        # Can't kick the leader
        if member == org.leader:
            caller.msg("|rYou cannot kick the organization leader.|n")
            return

        membership.is_active = False
        membership.save()

        caller.msg(f"|g{member.db_key} has been removed from {org.name}.|n")

        # Notify member
        if hasattr(member, 'msg'):
            member.msg(f"|r[ORGANIZATION]|n You have been removed from {org.name}.")

    def _transfer_leadership(self, org, caller):
        """Transfer leadership to another member."""
        if not self.rhs:
            caller.msg("Usage: +orgmanage <org>/transfer <member>")
            return

        # Only current leader can transfer (or GM)
        if org.leader != caller and not caller.permissions.get("Builder"):
            caller.msg("|rOnly the current leader can transfer leadership.|n")
            return

        member_name = self.rhs.strip()

        # Find member
        try:
            member = caller.search(member_name, global_search=True)
            if not member:
                return
            membership = OrganizationMembership.objects.get(
                organization=org,
                member=member,
                is_active=True,
                is_approved=True
            )
        except OrganizationMembership.DoesNotExist:
            caller.msg(f"|r{member_name} is not an active member of {org.name}.|n")
            return

        old_leader = org.leader
        org.leader = member
        org.save()

        caller.msg(f"|gLeadership of {org.name} transferred to {member.db_key}.|n")

        # Notify new leader
        if hasattr(member, 'msg'):
            member.msg(f"|g[ORGANIZATION]|n You are now the leader of {org.name}!")

        # Notify old leader
        if old_leader and old_leader != caller and hasattr(old_leader, 'msg'):
            old_leader.msg(f"|y[ORGANIZATION]|n {member.db_key} is now the leader of {org.name}.")


class CmdOrgCreate(Command):
    """
    Create a new organization (GM only).

    Usage:
      +orgcreate <name> = <type>

    Organization types:
      noble_house, witcher_school, trading_company, military_order,
      magical_academy, criminal_syndicate, guild, religious_order

    Example:
      +orgcreate House Foltest = noble_house
    """

    key = "+orgcreate"
    aliases = ["orgcreate"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        if not self.args or '=' not in self.args:
            caller.msg("Usage: +orgcreate <name> = <type>")
            caller.msg("\nValid types: noble_house, witcher_school, trading_company,")
            caller.msg("             military_order, magical_academy, criminal_syndicate,")
            caller.msg("             guild, religious_order")
            return

        org_name, org_type = self.args.split('=', 1)
        org_name = org_name.strip()
        org_type = org_type.strip().lower()

        # Validate type
        valid_types = [choice[0] for choice in OrganizationType.choices]
        if org_type not in valid_types:
            caller.msg(f"|rInvalid organization type: {org_type}|n")
            caller.msg("Valid types: " + ", ".join(valid_types))
            return

        # Check for duplicate
        if Organization.objects.filter(name__iexact=org_name).exists():
            caller.msg(f"|rAn organization named '{org_name}' already exists.|n")
            return

        # Create organization
        org = Organization.objects.create(
            name=org_name,
            organization_type=org_type,
            description="A newly created organization. Use +orgedit to add a description.",
            is_active=True
        )

        caller.msg(f"|gCreated organization: {org_name} ({org.get_organization_type_display()})|n")
        caller.msg(f"Use |w+orgedit {org_name}|n to configure it.")


class CmdOrgEdit(Command):
    """
    Edit organization properties (GM only).

    Usage:
      +orgedit <organization>/desc = <description>
      +orgedit <organization>/leader = <character>
      +orgedit <organization>/multiplier = <number>
      +orgedit <organization>/tithe = <percentage>
      +orgedit <organization>/leadershare = <percentage>
      +orgedit <organization>/approval = <yes|no>
      +orgedit <organization>/active = <yes|no>
      +orgedit <organization>/investment = <level>

    Examples:
      +orgedit House Foltest/desc = A prestigious noble house from Temeria.
      +orgedit House Foltest/multiplier = 2.0
      +orgedit House Foltest/tithe = 10
    """

    key = "+orgedit"
    aliases = ["orgedit"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        if not self.args or '=' not in self.args:
            caller.msg("Usage: +orgedit <organization>/property = <value>")
            return

        lhs, rhs = self.args.split('=', 1)
        rhs = rhs.strip()

        if '/' not in lhs:
            caller.msg("|rYou must specify a property to edit.|n")
            return

        org_name, prop = lhs.rsplit('/', 1)
        org_name = org_name.strip()
        prop = prop.strip().lower()

        # Find organization
        try:
            org = Organization.objects.get(name__iexact=org_name)
        except Organization.DoesNotExist:
            caller.msg(f"|rOrganization '{org_name}' not found.|n")
            return

        # Edit property
        if prop == "desc" or prop == "description":
            org.description = rhs
            org.save()
            caller.msg(f"|gUpdated description for {org.name}.|n")

        elif prop == "leader":
            leader = caller.search(rhs, global_search=True)
            if not leader:
                return
            org.leader = leader
            org.save()
            caller.msg(f"|g{leader.db_key} is now the leader of {org.name}.|n")

        elif prop == "multiplier":
            try:
                multiplier = float(rhs)
                org.base_income_multiplier = multiplier
                org.save()
                caller.msg(f"|gIncome multiplier set to {multiplier}x for {org.name}.|n")
            except ValueError:
                caller.msg("|rInvalid multiplier value.|n")

        elif prop == "tithe":
            try:
                percentage = int(rhs)
                if percentage < 0 or percentage > 100:
                    caller.msg("|rPercentage must be 0-100.|n")
                    return
                org.member_tithe_percentage = percentage
                org.save()
                caller.msg(f"|gMember tithing set to {percentage}% for {org.name}.|n")
            except ValueError:
                caller.msg("|rInvalid percentage value.|n")

        elif prop == "leadershare":
            try:
                percentage = int(rhs)
                if percentage < 0 or percentage > 100:
                    caller.msg("|rPercentage must be 0-100.|n")
                    return
                org.leader_share_percentage = percentage
                org.save()
                caller.msg(f"|gLeader share set to {percentage}% for {org.name}.|n")
            except ValueError:
                caller.msg("|rInvalid percentage value.|n")

        elif prop == "approval":
            if rhs.lower() in ('yes', 'true', '1'):
                org.requires_approval = True
                caller.msg(f"|g{org.name} now requires approval for new members.|n")
            else:
                org.requires_approval = False
                caller.msg(f"|g{org.name} no longer requires approval for new members.|n")
            org.save()

        elif prop == "active":
            if rhs.lower() in ('yes', 'true', '1'):
                org.is_active = True
                caller.msg(f"|g{org.name} is now active.|n")
            else:
                org.is_active = False
                caller.msg(f"|r{org.name} is now inactive.|n")
            org.save()

        elif prop == "investment":
            try:
                level = int(rhs)
                if level < 1:
                    caller.msg("|rInvestment level must be at least 1.|n")
                    return
                org.investment_level = level
                org.save()
                caller.msg(f"|gInvestment level set to {level} for {org.name}.|n")
            except ValueError:
                caller.msg("|rInvalid investment level.|n")

        else:
            caller.msg(f"|rUnknown property: {prop}|n")
            caller.msg("Valid properties: desc, leader, multiplier, tithe, leadershare, approval, active, investment")
