"""
OOC (Out of Character) Commands

This module contains the command set for OOC areas like the character
creation lobby. Only basic commands are available here.
"""

from evennia import default_cmds, CmdSet
from commands.request_commands import CmdRequestChar, CmdMyRequests


class OOCCmdSet(CmdSet):
    """
    Command set for OOC areas.

    Restricts available commands to:
    - Basic: look, who, quit, help
    - Character: requestchar, myrequests

    This cmdset replaces the normal character cmdset to prevent
    players from using in-game commands before character creation.
    """

    key = "OOCCmdSet"
    priority = 1
    mergetype = "Replace"  # Replace all other commands

    def at_cmdset_creation(self):
        """Populate the cmdset with allowed commands."""

        # Basic navigation and information
        self.add(default_cmds.CmdLook())
        self.add(default_cmds.CmdHelp())
        self.add(default_cmds.CmdQuit())

        # Communication
        self.add(default_cmds.CmdWho())

        # Character creation
        self.add(CmdRequestChar())
        self.add(CmdMyRequests())
