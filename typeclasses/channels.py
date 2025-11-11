"""
Custom channel types for Witcher RPG.

Includes organization channels that auto-manage subscriptions based on membership.
"""

from evennia.comms.comms import DefaultChannel
from world.witcher_rpg.organization_models import OrganizationMembership


class PublicChannel(DefaultChannel):
    """
    Public channel available to all players.
    """
    pass


class OrganizationChannel(DefaultChannel):
    """
    Channel locked to organization members.

    Automatically subscribes/unsubscribes members when they join/leave the organization.
    Access is controlled by active, approved membership in the linked organization.
    """

    def at_channel_creation(self):
        """Called when channel is first created."""
        super().at_channel_creation()
        # Store the organization name this channel is linked to
        if not self.db.organization_name:
            self.db.organization_name = None

    def access(self, accessing_obj, access_type='listen', default=False):
        """
        Check if accessing_obj has permission for this channel.

        Args:
            accessing_obj: The object trying to access the channel
            access_type: Type of access ('listen', 'send', 'control')
            default: Default return value if no org is set

        Returns:
            bool: True if access is granted
        """
        # Builders always have access
        if accessing_obj.locks.check_lockstring(accessing_obj, "dummy:perm(Builder)"):
            return True

        # Get the organization name
        org_name = self.db.organization_name
        if not org_name:
            return default

        # Check if accessing_obj is an active, approved member
        try:
            membership = OrganizationMembership.objects.get(
                organization__name=org_name,
                member=accessing_obj,
                is_active=True,
                is_approved=True
            )
            return True
        except OrganizationMembership.DoesNotExist:
            return False

    def channel_prefix(self, msg=None, emit=False):
        """
        Format the channel prefix.

        Returns a custom prefix that includes the organization name.
        """
        org_name = self.db.organization_name or self.key
        return f"|c[{org_name}]|n "

    def at_pre_msg(self, message, **kwargs):
        """Hook called before message is distributed."""
        # Could add logging or filtering here
        pass

    def at_post_msg(self, message, **kwargs):
        """Hook called after message is distributed."""
        # Could add notifications or other post-processing here
        pass


class FactionChannel(DefaultChannel):
    """
    Channel for country or faction-based groups.

    Access controlled by character's country, vocation, or other faction criteria.
    """

    def at_channel_creation(self):
        """Called when channel is first created."""
        super().at_channel_creation()
        # Store faction criteria
        if not self.db.faction_type:
            self.db.faction_type = None  # 'country', 'vocation', etc.
        if not self.db.faction_value:
            self.db.faction_value = None  # 'Temeria', 'Witcher', etc.

    def access(self, accessing_obj, access_type='listen', default=False):
        """
        Check if accessing_obj meets faction criteria.

        Args:
            accessing_obj: The object trying to access
            access_type: Type of access
            default: Default return value

        Returns:
            bool: True if access is granted
        """
        # Builders always have access
        if accessing_obj.locks.check_lockstring(accessing_obj, "dummy:perm(Builder)"):
            return True

        faction_type = self.db.faction_type
        faction_value = self.db.faction_value

        if not faction_type or not faction_value:
            return default

        # Get character data
        from world.witcher_rpg.models import WitcherCharacter
        try:
            character = WitcherCharacter.objects.get(db_object=accessing_obj)
        except WitcherCharacter.DoesNotExist:
            return False

        # Check faction criteria
        if faction_type == 'country':
            return character.country == faction_value
        elif faction_type == 'vocation':
            return character.vocation.name == faction_value
        elif faction_type == 'social_rank':
            return character.social_rank >= int(faction_value)

        return False

    def channel_prefix(self, msg=None, emit=False):
        """Format the channel prefix."""
        faction_value = self.db.faction_value or self.key
        return f"|m[{faction_value}]|n "


class PrivateChannel(DefaultChannel):
    """
    Private channel that players can create for temporary groups.

    Owner controls who can join/speak.
    """

    def at_channel_creation(self):
        """Called when channel is first created."""
        super().at_channel_creation()
        if not self.db.owner:
            self.db.owner = None
        if not self.db.allowed_members:
            self.db.allowed_members = []

    def access(self, accessing_obj, access_type='listen', default=False):
        """Check if accessing_obj is owner or allowed member."""
        # Owner always has access
        if self.db.owner == accessing_obj:
            return True

        # Check allowed members list
        if accessing_obj in self.db.allowed_members:
            return True

        # Builders have access to control
        if access_type == 'control':
            return accessing_obj.locks.check_lockstring(accessing_obj, "dummy:perm(Builder)")

        return False

    def channel_prefix(self, msg=None, emit=False):
        """Format the channel prefix."""
        return f"|y[Private:{self.key}]|n "
