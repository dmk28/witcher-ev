"""
Mission and extraction commands for Witcher RPG.
Handles resource extraction, mission creation, DM assignment, and mission completion.
"""

from evennia import Command
from django.utils import timezone
from world.witcher_rpg.room_models import (
    WitcherRoom, Mission, MissionLog, ExtractionResource, DangerLevel
)
from world.witcher_rpg.loot_system import LootGenerator, ExtractionSystem


class CmdExtract(Command):
    """
    Extract resources from the environment.

    Usage:
      extract <resource name>
      extract/list

    Extracts resources from extraction rooms. Success depends on your
    Perception and Athletics skills. Extracting resources increases the
    danger timer, which may eventually spawn a mission.

    Available resources depend on the biome:
    - Forest: Herbs, wood, game
    - Mine: Ore, gems, minerals
    - Hills: Stone, clay
    - River/Ocean: Fish, shells
    - etc.
    """

    key = "extract"
    aliases = []
    locks = "cmd:all()"
    help_category = "Missions"

    def func(self):
        caller = self.caller

        if not hasattr(caller, 'db_character') or not caller.db_character:
            caller.msg("You don't have a character sheet.")
            return

        if not caller.location:
            caller.msg("You need to be in a location to extract resources.")
            return

        # Get witcher room
        try:
            witcher_room = WitcherRoom.objects.get(room_object=caller.location)
        except WitcherRoom.DoesNotExist:
            caller.msg("This location doesn't support resource extraction.")
            return

        # Check if extraction room
        if witcher_room.room_type != 'extraction':
            caller.msg("This is not an extraction room. You cannot gather resources here.")
            return

        # List available resources
        if 'list' in self.switches:
            self._list_resources(witcher_room)
            return

        if not self.args:
            caller.msg("Usage: extract <resource name>  OR  extract/list")
            return

        resource_name = self.args.strip()

        # Get available resources in this biome
        available = ExtractionResource.objects.filter(biome=witcher_room.biome)

        # Try exact match
        resource = None
        for res in available:
            if res.resource_name.lower() == resource_name.lower():
                resource = res
                break

        # Try partial match
        if not resource:
            for res in available:
                if resource_name.lower() in res.resource_name.lower():
                    resource = res
                    break

        if not resource:
            caller.msg(f"No resource named '{resource_name}' found in this {witcher_room.get_biome_display()}.")
            caller.msg("Use 'extract/list' to see available resources.")
            return

        # Attempt extraction
        result = ExtractionSystem.attempt_extraction(caller, witcher_room, resource.resource_name)

        if result['success']:
            caller.msg(f"|g{result['message']}|n")
            caller.msg(f"Roll: {result['roll_result']['message']}")
            caller.msg(f"Danger increased by {result['danger_increased']}. Current danger timer: {witcher_room.extraction_timer}/100")

            if result['became_mission']:
                caller.location.msg_contents(
                    f"|r[!] The danger in this area has reached critical levels! A mission has spawned.|n"
                )
        else:
            caller.msg(f"|r{result['message']}|n")
            if 'roll_result' in result:
                caller.msg(f"Roll: {result['roll_result']['message']}")

    def _list_resources(self, witcher_room):
        """List available resources in this biome."""
        resources = ExtractionResource.objects.filter(biome=witcher_room.biome)

        if not resources.exists():
            self.caller.msg(f"No extractable resources in this {witcher_room.get_biome_display()}.")
            return

        output = []
        output.append("|w" + "=" * 70 + "|n")
        output.append("|w" + f"{'Resources in ' + witcher_room.get_biome_display():^70}" + "|n")
        output.append("|w" + "=" * 70 + "|n")
        output.append(f"|yDanger Timer:|n {witcher_room.extraction_timer}/100")
        output.append("")

        for res in resources:
            output.append(f"|y{res.resource_name}|n")
            output.append(f"  Difficulty: CR {res.extraction_difficulty}")
            output.append(f"  Yield: {res.base_quantity_min}-{res.base_quantity_max} per extraction")
            output.append(f"  Danger Increase: +{res.danger_increase_per_extraction}")
            output.append("")

        output.append("|w" + "=" * 70 + "|n")
        self.caller.msg("\n".join(output))


class CmdMission(Command):
    """
    Manage missions and plot events.

    Usage:
      mission                              - View active mission in room
      mission/create <danger>=<name>       - Create mission (Storyteller only)
      mission/dm                           - Volunteer as DM for mission
      mission/join                         - Join active mission
      mission/complete                     - Complete mission (DM only)
      mission/cancel                       - Cancel mission (Storyteller only)

    Danger levels: safe, low, moderate, high, critical

    DM receives 2 XP only. Participants receive gold, XP, and loot based
    on danger level. Critical missions have 10% chance for Tier IV artifacts.
    Plot missions have 2.5x artifact multiplier and 1.5x gold/XP.

    Examples:
      mission/create critical=Rescue Ciri from Nilfgaard
      mission/create moderate=Bandit Ambush
      mission/dm
      mission/join
      mission/complete
    """

    key = "mission"
    aliases = []
    locks = "cmd:all()"
    help_category = "Missions"

    def func(self):
        caller = self.caller

        if not caller.location:
            caller.msg("You need to be in a location to manage missions.")
            return

        # Get witcher room
        try:
            witcher_room = WitcherRoom.objects.get(room_object=caller.location)
        except WitcherRoom.DoesNotExist:
            caller.msg("This location doesn't support missions.")
            return

        # View mission status
        if not self.switches:
            self._view_mission(witcher_room)
            return

        # Create mission
        if 'create' in self.switches:
            self._create_mission(witcher_room)
            return

        # Volunteer as DM
        if 'dm' in self.switches:
            self._volunteer_dm(witcher_room)
            return

        # Join mission
        if 'join' in self.switches:
            self._join_mission(witcher_room)
            return

        # Complete mission
        if 'complete' in self.switches:
            self._complete_mission(witcher_room)
            return

        # Cancel mission
        if 'cancel' in self.switches:
            self._cancel_mission(witcher_room)
            return

        caller.msg("Invalid mission command. See 'help mission'.")

    def _view_mission(self, witcher_room):
        """View active mission in room."""
        active_missions = Mission.objects.filter(
            room=witcher_room,
            is_active=True
        )

        if not active_missions.exists():
            self.caller.msg(f"|yNo active missions in this location.|n")
            if witcher_room.room_type == 'extraction':
                self.caller.msg(f"Danger Timer: {witcher_room.extraction_timer}/100")
            return

        mission = active_missions.first()

        output = []
        output.append("|w" + "=" * 70 + "|n")
        output.append("|w" + f"{'Mission: ' + mission.name:^70}" + "|n")
        output.append("|w" + "=" * 70 + "|n")
        output.append(f"|yDanger Level:|n {mission.get_danger_level_display()}")
        output.append(f"|yPlot Mission:|n {'Yes (2.5x artifacts, 1.5x rewards)' if mission.is_plot_mission else 'No'}")
        output.append("")
        output.append(f"|yDescription:|n")
        output.append(mission.description)
        output.append("")

        if mission.dungeon_master:
            output.append(f"|yDungeon Master:|n {mission.dungeon_master.db_key}")
        else:
            output.append("|yDungeon Master:|n |rNone assigned|n (use 'mission/dm' to volunteer)")

        output.append("")
        output.append(f"|yRewards:|n")
        output.append(f"  Gold: {mission.base_gold_reward}")
        output.append(f"  Experience: {mission.experience_reward} XP")
        output.append(f"  Loot: Based on tier weights")

        participants = mission.participants.all()
        if participants:
            output.append("")
            output.append(f"|yParticipants ({participants.count()}):|n")
            for participant in participants:
                output.append(f"  - {participant.db_key}")

        output.append("")
        output.append("|w" + "=" * 70 + "|n")
        self.caller.msg("\n".join(output))

    def _create_mission(self, witcher_room):
        """Create a new mission (Storyteller/Admin only)."""
        if not self.caller.check_permstring("Builder"):
            self.caller.msg("|rOnly Storytellers can create missions.|n")
            return

        if not self.args or '=' not in self.args:
            self.caller.msg("Usage: mission/create <danger>=<name>")
            self.caller.msg("Danger levels: safe, low, moderate, high, critical")
            self.caller.msg("Example: mission/create critical=Rescue Ciri from Nilfgaard")
            return

        parts = self.args.split('=', 1)
        danger = parts[0].strip().lower()
        name = parts[1].strip()

        # Validate danger level
        danger_map = {
            'safe': DangerLevel.SAFE,
            'low': DangerLevel.LOW,
            'moderate': DangerLevel.MODERATE,
            'high': DangerLevel.HIGH,
            'critical': DangerLevel.CRITICAL
        }

        if danger not in danger_map:
            self.caller.msg(f"Invalid danger level '{danger}'. Use: safe, low, moderate, high, critical")
            return

        danger_level = danger_map[danger]

        # Create mission
        mission = Mission.objects.create(
            room=witcher_room,
            name=name,
            description="(Set description in admin panel)",
            danger_level=danger_level,
            is_plot_mission=self.caller.check_permstring("Admin"),  # Admins create plot missions
            is_active=True
        )

        # Set loot weights and rewards
        mission.set_default_loot_weights()
        mission.calculate_rewards()

        # Mark room as mission active
        witcher_room.is_mission_active = True
        witcher_room.danger_level = danger_level
        witcher_room.save()

        self.caller.msg(f"|gCreated mission: {name} ({mission.get_danger_level_display()})|n")
        self.caller.msg(f"Rewards: {mission.base_gold_reward}g, {mission.experience_reward} XP")
        self.caller.msg(f"Plot Mission: {'Yes' if mission.is_plot_mission else 'No'}")

        self.caller.location.msg_contents(
            f"|y[!] A new mission has been posted: {name}|n",
            exclude=self.caller
        )

    def _volunteer_dm(self, witcher_room):
        """Volunteer as DM for active mission."""
        if not hasattr(self.caller, 'db_character') or not self.caller.db_character:
            self.caller.msg("You don't have a character sheet.")
            return

        active_missions = Mission.objects.filter(
            room=witcher_room,
            is_active=True
        )

        if not active_missions.exists():
            self.caller.msg("No active mission in this location.")
            return

        mission = active_missions.first()

        if mission.dungeon_master:
            self.caller.msg(f"This mission already has a DM: {mission.dungeon_master.db_key}")
            return

        # Assign DM
        mission.dungeon_master = self.caller
        mission.save()

        self.caller.msg(f"|gYou are now the Dungeon Master for '{mission.name}'.|n")
        self.caller.msg("|yAs DM, you will receive 2 XP upon completion but no loot or gold.|n")

        self.caller.location.msg_contents(
            f"|y{self.caller.db_key} has volunteered as Dungeon Master for '{mission.name}'.|n",
            exclude=self.caller
        )

    def _join_mission(self, witcher_room):
        """Join active mission."""
        if not hasattr(self.caller, 'db_character') or not self.caller.db_character:
            self.caller.msg("You don't have a character sheet.")
            return

        active_missions = Mission.objects.filter(
            room=witcher_room,
            is_active=True
        )

        if not active_missions.exists():
            self.caller.msg("No active mission in this location.")
            return

        mission = active_missions.first()

        # Check if already DM
        if mission.dungeon_master == self.caller:
            self.caller.msg("|rYou are the DM for this mission and cannot participate.|n")
            return

        # Check if already joined
        if mission.participants.filter(id=self.caller.id).exists():
            self.caller.msg("You have already joined this mission.")
            return

        # Join mission
        mission.participants.add(self.caller)
        mission.save()

        # Create log
        MissionLog.objects.create(
            mission=mission,
            character=self.caller,
            action_type='joined',
            description=f"{self.caller.db_key} joined the mission"
        )

        self.caller.msg(f"|gYou have joined the mission: {mission.name}|n")
        self.caller.location.msg_contents(
            f"|y{self.caller.db_key} has joined the mission!|n",
            exclude=self.caller
        )

    def _complete_mission(self, witcher_room):
        """Complete mission and distribute rewards (DM only)."""
        if not hasattr(self.caller, 'db_character') or not self.caller.db_character:
            self.caller.msg("You don't have a character sheet.")
            return

        active_missions = Mission.objects.filter(
            room=witcher_room,
            is_active=True
        )

        if not active_missions.exists():
            self.caller.msg("No active mission in this location.")
            return

        mission = active_missions.first()

        # Check if caller is DM
        if mission.dungeon_master != self.caller:
            self.caller.msg("|rOnly the Dungeon Master can complete the mission.|n")
            return

        participants = list(mission.participants.all())

        if not participants:
            self.caller.msg("|rNo participants to reward. Mission cannot be completed.|n")
            return

        # Distribute rewards
        rewards = LootGenerator.complete_mission_rewards(
            mission,
            participants,
            dm=self.caller
        )

        # Mark mission complete
        mission.is_active = False
        mission.is_completed = True
        mission.completed_date = timezone.now()
        mission.save()

        # Update room
        witcher_room.is_mission_active = False
        if witcher_room.room_type == 'extraction':
            witcher_room.extraction_timer = 0  # Reset timer
        witcher_room.save()

        # Announce completion
        output = []
        output.append("|w" + "=" * 70 + "|n")
        output.append("|w" + f"{'Mission Complete: ' + mission.name:^70}" + "|n")
        output.append("|w" + "=" * 70 + "|n")
        output.append("")

        # DM rewards
        if rewards['dm']:
            output.append(f"|yDungeon Master ({self.caller.db_key}):|n")
            output.append(f"  +{rewards['dm']['xp']} XP")
            output.append("")

        # Participant rewards
        output.append("|yParticipant Rewards:|n")
        for char_key, char_rewards in rewards['participants'].items():
            output.append(f"\n|g{char_key}:|n")
            output.append(f"  +{char_rewards['gold']} gold")
            output.append(f"  +{char_rewards['xp']} XP")
            if char_rewards['items']:
                output.append(f"  Items:")
                for item_name in char_rewards['items']:
                    output.append(f"    - {item_name}")

        output.append("")
        output.append("|w" + "=" * 70 + "|n")

        # Send to room
        self.caller.location.msg_contents("\n".join(output))

        # Create mission logs
        for participant in participants:
            char_rewards = rewards['participants'].get(participant.db_key, {})
            MissionLog.objects.create(
                mission=mission,
                character=participant,
                action_type='completed',
                description=f"{participant.db_key} completed the mission",
                rewards_received=char_rewards
            )

    def _cancel_mission(self, witcher_room):
        """Cancel mission (Storyteller only)."""
        if not self.caller.check_permstring("Builder"):
            self.caller.msg("|rOnly Storytellers can cancel missions.|n")
            return

        active_missions = Mission.objects.filter(
            room=witcher_room,
            is_active=True
        )

        if not active_missions.exists():
            self.caller.msg("No active mission in this location.")
            return

        mission = active_missions.first()

        # Cancel mission
        mission.is_active = False
        mission.save()

        # Update room
        witcher_room.is_mission_active = False
        witcher_room.save()

        self.caller.msg(f"|yMission '{mission.name}' has been cancelled.|n")
        self.caller.location.msg_contents(
            f"|r[!] The mission '{mission.name}' has been cancelled.|n",
            exclude=self.caller
        )
