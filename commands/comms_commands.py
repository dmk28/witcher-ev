"""
Communication commands for Witcher RPG.

Includes paging and channel management commands.
"""

from evennia import Command, create_channel
from evennia.comms.models import ChannelDB
from world.witcher_rpg.mush_utils import convert_mush_tokens
from django.utils import timezone
from datetime import timedelta


class CmdPage(Command):
    """
    Send a private message to another player.

    Usage:
      +page <player> = <message>
      +page <player1>,<player2> = <message>
      page <player> = <message>

    Sends a private message to one or more players. Messages are prefixed
    with [Page] and include timestamps.

    You can also use: tell, +tell
    """

    key = "+page"
    aliases = ["page", "tell", "+tell"]
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        caller = self.caller

        if not self.args or '=' not in self.args:
            caller.msg("Usage: +page <player> = <message>")
            return

        # Parse targets and message
        lhs, message = self.args.split('=', 1)
        message = message.strip()
        target_names = [name.strip() for name in lhs.split(',')]

        if not message:
            caller.msg("|rYou must provide a message to send.|n")
            return

        # Find all targets
        targets = []
        not_found = []

        for name in target_names:
            target = caller.search(name, global_search=True)
            if target:
                # Check if it's a character (not a room or object)
                if target.has_account:
                    targets.append(target)
                else:
                    not_found.append(name)
            else:
                not_found.append(name)

        if not_found:
            caller.msg(f"|rCould not find:|n {', '.join(not_found)}")

        if not targets:
            caller.msg("|rNo valid targets found.|n")
            return

        # Format timestamp
        timestamp = timezone.now().strftime("%H:%M")

        # Send to each target
        for target in targets:
            # Check if target is AFK/busy
            is_afk = target.db.afk
            is_busy = target.db.busy

            if is_afk:
                caller.msg(f"|y{target.key} is AFK:|n {target.db.afk_message or 'Away from keyboard'}")
            elif is_busy:
                caller.msg(f"|y{target.key} is Busy:|n {target.db.busy_message or 'Do not disturb'}")

            # Format message for target
            target_msg = f"|c[Page from {caller.key} at {timestamp}]|n {message}"
            target.msg(convert_mush_tokens(target_msg))

            # Store in target's page history
            if not target.db.page_history:
                target.db.page_history = []
            target.db.page_history.append({
                'from': caller.key,
                'message': message,
                'timestamp': timezone.now(),
                'direction': 'received'
            })
            # Keep only last 50 pages
            target.db.page_history = target.db.page_history[-50:]

        # Confirm to sender
        if len(targets) == 1:
            caller_msg = f"|c[Page to {targets[0].key} at {timestamp}]|n {message}"
        else:
            names = ', '.join([t.key for t in targets])
            caller_msg = f"|c[Page to {names} at {timestamp}]|n {message}"

        caller.msg(convert_mush_tokens(caller_msg))

        # Store in caller's page history
        if not caller.db.page_history:
            caller.db.page_history = []
        caller.db.page_history.append({
            'to': ', '.join([t.key for t in targets]),
            'message': message,
            'timestamp': timezone.now(),
            'direction': 'sent'
        })
        caller.db.page_history = caller.db.page_history[-50:]


class CmdPageHistory(Command):
    """
    View your recent page history.

    Usage:
      +pagehistory [number]
      +ph [number]

    Shows your recent page messages. Optionally specify how many to show (default: 10).
    """

    key = "+pagehistory"
    aliases = ["+ph", "pagehistory"]
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        caller = self.caller

        # Get number of messages to show
        try:
            count = int(self.args.strip()) if self.args else 10
            count = max(1, min(count, 50))  # Between 1 and 50
        except ValueError:
            caller.msg("|rInvalid number.|n")
            return

        history = caller.db.page_history or []

        if not history:
            caller.msg("|yYou have no page history.|n")
            return

        # Show most recent messages
        recent = history[-count:]

        lines = []
        lines.append("%r")
        lines.append("=" * 70)
        lines.append(f"Page History (Last {len(recent)} messages)")
        lines.append("=" * 70)
        lines.append("%r")

        for entry in recent:
            timestamp = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            direction = entry['direction']
            message = entry['message']

            if direction == 'sent':
                to_whom = entry.get('to', 'Unknown')
                lines.append(f"|c[{timestamp}] To {to_whom}:|n")
            else:
                from_whom = entry.get('from', 'Unknown')
                lines.append(f"|c[{timestamp}] From {from_whom}:|n")

            lines.append(f"%t%t{message}")
            lines.append("%r")

        lines.append("=" * 70)
        lines.append("%r")

        caller.msg(convert_mush_tokens("%r".join(lines)))


class CmdAfk(Command):
    """
    Set yourself as Away From Keyboard.

    Usage:
      +afk [message]
      +afk/clear

    Sets an AFK status. Others who page you will see your AFK message.
    Use /clear or no message to remove AFK status.
    """

    key = "+afk"
    aliases = ["afk"]
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        caller = self.caller

        if "clear" in self.switches or not self.args:
            caller.db.afk = False
            caller.db.afk_message = None
            caller.msg("|gAFK status cleared.|n")
            return

        message = self.args.strip()
        caller.db.afk = True
        caller.db.afk_message = message

        caller.msg(f"|gAFK status set:|n {message}")


class CmdBusy(Command):
    """
    Set yourself as Busy/Do Not Disturb.

    Usage:
      +busy [message]
      +busy/clear

    Sets a busy status. Others who page you will see your busy message.
    Use /clear or no message to remove busy status.
    """

    key = "+busy"
    aliases = ["busy"]
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        caller = self.caller

        if "clear" in self.switches or not self.args:
            caller.db.busy = False
            caller.db.busy_message = None
            caller.msg("|gBusy status cleared.|n")
            return

        message = self.args.strip()
        caller.db.busy = True
        caller.db.busy_message = message

        caller.msg(f"|gBusy status set:|n {message}")


class CmdChannels(Command):
    """
    List all channels available to you.

    Usage:
      +channels
      +channels/all

    Shows all channels you can access. Use /all to see all channels
    in the game (including ones you can't access).
    """

    key = "+channels"
    aliases = ["channels", "+chan"]
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        caller = self.caller

        if "all" in self.switches:
            # Show all channels
            channels = ChannelDB.objects.all()
            title = "All Channels"
        else:
            # Show only accessible channels
            channels = [ch for ch in ChannelDB.objects.all() if ch.access(caller, 'listen')]
            title = "Your Channels"

        if not channels:
            caller.msg("|yNo channels found.|n")
            return

        lines = []
        lines.append("%r")
        lines.append("=" * 70)
        lines.append(title)
        lines.append("=" * 70)
        lines.append("%r")

        for ch in channels:
            # Check if subscribed
            is_subscribed = ch.has_connection(caller)
            sub_marker = "|g✓|n" if is_subscribed else "|r✗|n"

            # Get channel type
            typeclass = ch.typeclass_path.split('.')[-1] if ch.typeclass_path else "Channel"

            # Get subscriber count
            sub_count = len(ch.subscriptions.all())

            lines.append(f"{sub_marker} |w{ch.key}|n ({typeclass}) - {sub_count} subscribers")

            # Show description if available
            if ch.db.desc:
                lines.append(f"%t%t{ch.db.desc}")

            lines.append("%r")

        lines.append("=" * 70)
        lines.append("%r")
        lines.append("Use |wchannel <name> = <message>|n to send to a channel.")
        lines.append("Use |waddcom <alias> = <channel>|n to create a channel alias.")
        lines.append("%r")

        caller.msg(convert_mush_tokens("%r".join(lines)))


class CmdChannelCreate(Command):
    """
    Create a new organization or private channel (GM only).

    Usage:
      +channelcreate <name> = <type>
      +channelcreate <name> = org:<organization name>
      +channelcreate <name> = faction:<country/vocation>

    Types:
      public - Public channel anyone can join
      org:<name> - Organization channel (auto-manages members)
      faction:<value> - Faction channel (country or vocation)
      private - Private channel with owner control

    Examples:
      +channelcreate houseFoltest = org:House Foltest
      +channelcreate temeria = faction:Temeria
      +channelcreate staff = private
    """

    key = "+channelcreate"
    aliases = ["channelcreate"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        if not self.args or '=' not in self.args:
            caller.msg("Usage: +channelcreate <name> = <type>")
            return

        channel_name, channel_type = self.args.split('=', 1)
        channel_name = channel_name.strip()
        channel_type = channel_type.strip().lower()

        # Check if channel exists
        if ChannelDB.objects.filter(db_key=channel_name).exists():
            caller.msg(f"|rChannel '{channel_name}' already exists.|n")
            return

        # Determine typeclass
        if channel_type == 'public':
            typeclass = 'typeclasses.channels.PublicChannel'
            extras = {}
        elif channel_type.startswith('org:'):
            org_name = channel_type[4:].strip()
            typeclass = 'typeclasses.channels.OrganizationChannel'
            extras = {'organization_name': org_name}
        elif channel_type.startswith('faction:'):
            faction_value = channel_type[8:].strip()
            typeclass = 'typeclasses.channels.FactionChannel'
            # Determine if it's a country or vocation
            from world.witcher_rpg.models import WitcherCharacter
            if faction_value in WitcherCharacter.COUNTRIES:
                extras = {'faction_type': 'country', 'faction_value': faction_value}
            else:
                extras = {'faction_type': 'vocation', 'faction_value': faction_value}
        elif channel_type == 'private':
            typeclass = 'typeclasses.channels.PrivateChannel'
            extras = {'owner': caller}
        else:
            caller.msg("|rInvalid channel type.|n")
            return

        # Create channel
        channel = create_channel(
            channel_name,
            desc=f"Channel: {channel_name}",
            typeclass=typeclass
        )

        # Set extra attributes
        for key, value in extras.items():
            channel.db.__setattr__(key, value)

        caller.msg(f"|gCreated channel:|n {channel_name} ({channel_type})")

        # Auto-subscribe creator to private channels
        if channel_type == 'private':
            channel.connect(caller)
            caller.msg(f"|gYou have been subscribed to {channel_name}.|n")


class CmdChannelDelete(Command):
    """
    Delete a channel (GM only).

    Usage:
      +channeldelete <name>

    Permanently deletes a channel. This cannot be undone.
    """

    key = "+channeldelete"
    aliases = ["channeldelete"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +channeldelete <name>")
            return

        channel_name = self.args.strip()

        try:
            channel = ChannelDB.objects.get(db_key=channel_name)
        except ChannelDB.DoesNotExist:
            caller.msg(f"|rChannel '{channel_name}' not found.|n")
            return

        # Delete the channel
        channel.delete()
        caller.msg(f"|gDeleted channel:|n {channel_name}")
