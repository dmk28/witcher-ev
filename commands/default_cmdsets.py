"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from commands.combat_commands import (
    CmdCombatStart,
    CmdAttack,
    CmdCast,
    CmdStance,
    CmdCombatStatus
)
from commands.inventory_commands import (
    CmdInventory,
    CmdEquip,
    CmdUnequip,
    CmdUse,
    CmdGive,
    CmdBank,
    CmdCraft
)
from commands.mission_commands import (
    CmdExtract,
    CmdMission
)
from commands.room_commands import (
    CmdRoom
)
from commands.social_commands import (
    CmdSocialStart,
    CmdSocialAction,
    CmdSocialStance,
    CmdSocialStatus
)
from commands.shop_commands import (
    CmdBrowse,
    CmdBuy,
    CmdSell,
    CmdHaggle,
    CmdShopManage
)
from commands.advancement_commands import (
    CmdAdvance,
    CmdRequest,
    CmdApprove,
    CmdAdvancementHistory
)
from commands.crafting_commands import (
    CmdRecipes,
    CmdCraft as CmdCraftRecipe,
    CmdLearnRecipe,
    CmdSetBonus,
    CmdCraftingHistory
)
from commands.request_commands import (
    CmdRequestChar,
    CmdGMRequests,
    CmdApproveRequest,
    CmdDenyRequest,
    CmdMyRequests
)
from commands.building_commands import (
    CmdRoomCreate,
    CmdRoomEdit,
    CmdRoomLink,
    CmdRoomDelete,
    CmdBuyRoom,
    CmdMyRooms,
    CmdRoomPurpose,
    CmdSellRoom
)
from commands.income_commands import (
    CmdIncome,
    CmdOrganizations,
    CmdOrgJoin,
    CmdOrgLeave,
    CmdOrgInvest,
    CmdOrgManage,
    CmdOrgCreate,
    CmdOrgEdit
)


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #

        # Add Witcher RPG combat commands
        self.add(CmdCombatStart())
        self.add(CmdAttack())
        self.add(CmdCast())
        self.add(CmdStance())
        self.add(CmdCombatStatus())

        # Add Witcher RPG inventory commands
        self.add(CmdInventory())
        self.add(CmdEquip())
        self.add(CmdUnequip())
        self.add(CmdUse())
        self.add(CmdGive())
        self.add(CmdBank())
        self.add(CmdCraft())

        # Add Witcher RPG mission commands
        self.add(CmdExtract())
        self.add(CmdMission())

        # Add Witcher RPG room commands
        self.add(CmdRoom())

        # Add Witcher RPG social combat commands
        self.add(CmdSocialStart())
        self.add(CmdSocialAction())
        self.add(CmdSocialStance())
        self.add(CmdSocialStatus())

        # Add Witcher RPG shop commands
        self.add(CmdBrowse())
        self.add(CmdBuy())
        self.add(CmdSell())
        self.add(CmdHaggle())
        self.add(CmdShopManage())

        # Add Witcher RPG advancement commands
        self.add(CmdAdvance())
        self.add(CmdRequest())
        self.add(CmdApprove())
        self.add(CmdAdvancementHistory())

        # Add Witcher RPG crafting commands
        self.add(CmdRecipes())
        self.add(CmdCraftRecipe())
        self.add(CmdLearnRecipe())
        self.add(CmdSetBonus())
        self.add(CmdCraftingHistory())

        # Add Witcher RPG request commands
        self.add(CmdRequestChar())
        self.add(CmdGMRequests())
        self.add(CmdApproveRequest())
        self.add(CmdDenyRequest())
        self.add(CmdMyRequests())

        # Add Witcher RPG building commands
        # GM commands
        self.add(CmdRoomCreate())
        self.add(CmdRoomEdit())
        self.add(CmdRoomLink())
        self.add(CmdRoomDelete())
        # Player commands
        self.add(CmdBuyRoom())
        self.add(CmdMyRooms())
        self.add(CmdRoomPurpose())
        self.add(CmdSellRoom())

        # Add Witcher RPG income/organization commands
        # Player commands
        self.add(CmdIncome())
        self.add(CmdOrganizations())
        self.add(CmdOrgJoin())
        self.add(CmdOrgLeave())
        self.add(CmdOrgInvest())
        self.add(CmdOrgManage())
        # GM commands
        self.add(CmdOrgCreate())
        self.add(CmdOrgEdit())


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
