"""
Combat commands for Witcher RPG turn-based combat system.
"""
from evennia import Command
from evennia.commands.default.muxcommand import MuxCommand
from world.witcher_rpg.combat import CombatEngine
from world.witcher_rpg.combat_models import CombatEncounter, CombatParticipant


class CmdCombatStart(MuxCommand):
    """
    Start a combat encounter in this room.

    Usage:
      combat/start [<name>]
      combat/join
      combat/leave
      combat/end

    Switches:
      start - Start a new combat encounter
      join  - Join the active combat in this room
      leave - Leave combat
      end   - End the combat (GM only)

    Examples:
      combat/start Bandit Ambush
      combat/join
      combat/leave

    This starts turn-based combat tracking. All participants
    will roll initiative and combat will proceed in turn order.
    """

    key = "combat"
    aliases = ["fight"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        location = caller.location

        if not location:
            caller.msg("|rYou need to be in a location to use combat commands.|n")
            return

        # Check for switches
        if "start" in self.switches:
            self.start_combat()
        elif "join" in self.switches:
            self.join_combat()
        elif "leave" in self.switches:
            self.leave_combat()
        elif "end" in self.switches:
            self.end_combat()
        else:
            caller.msg("Usage: combat/start, combat/join, combat/leave, or combat/end")

    def start_combat(self):
        """Start a new combat encounter."""
        caller = self.caller
        location = caller.location

        # Check if combat already exists
        existing = CombatEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if existing:
            caller.msg("|rCombat is already active in this room!|n")
            caller.msg("Use 'combat/join' to join the existing combat.")
            return

        # Create combat encounter
        name = self.args.strip() or f"Combat in {location.name}"
        encounter = CombatEncounter.objects.create(
            name=name,
            location=location,
            is_active=True
        )

        location.msg_contents(
            f"|y{'=' * 70}|n\n"
            f"|rCOMBAT STARTED: {name}|n\n"
            f"|y{'=' * 70}|n\n"
            f"Use |wcombat/join|n to enter combat!\n"
        )

        # Auto-join the starter
        self.join_combat(encounter)

    def join_combat(self, encounter=None):
        """Join an active combat encounter."""
        caller = self.caller
        location = caller.location

        if not encounter:
            encounter = CombatEncounter.objects.filter(
                location=location,
                is_active=True
            ).first()

        if not encounter:
            caller.msg("|rNo active combat in this room!|n")
            caller.msg("Use 'combat/start' to begin combat.")
            return

        # Check if already in combat
        existing = CombatParticipant.objects.filter(
            encounter=encounter,
            character=caller,
            is_active=True
        ).first()

        if existing:
            caller.msg("|rYou are already in combat!|n")
            return

        # Check if character is set up
        if not hasattr(caller, 'db_character') or not caller.db_character:
            caller.msg("|rYou need a character sheet to enter combat!|n")
            return

        # Roll initiative
        init_roll = CombatEngine.roll_initiative(caller)

        # Determine max HP (Endurance * 10 for now)
        max_hp = caller.get_stat('endurance') * 10

        # Create participant
        participant = CombatParticipant.objects.create(
            encounter=encounter,
            character=caller,
            initiative_roll=init_roll,
            current_hp=max_hp,
            max_hp=max_hp,
            stance='moderate'
        )

        # Assign initiative order
        participants = encounter.participants.filter(is_active=True).order_by(
            '-initiative_roll', 'id'
        )

        for i, p in enumerate(participants):
            p.initiative_order = i
            p.save()

        location.msg_contents(
            f"|g{caller.name}|n joins combat! "
            f"(Initiative: |y{init_roll}|n, HP: |g{max_hp}|n)"
        )

        # Show combat status
        status = CombatEngine.format_combat_status(encounter)
        location.msg_contents(status)

    def leave_combat(self):
        """Leave combat."""
        caller = self.caller
        location = caller.location

        encounter = CombatEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if not encounter:
            caller.msg("|rNo active combat in this room!|n")
            return

        participant = CombatParticipant.objects.filter(
            encounter=encounter,
            character=caller,
            is_active=True
        ).first()

        if not participant:
            caller.msg("|rYou are not in combat!|n")
            return

        participant.is_active = False
        participant.save()

        location.msg_contents(f"|y{caller.name}|n has left combat.")

        # Check if combat should end
        active_count = encounter.participants.filter(is_active=True).count()
        if active_count <= 1:
            encounter.is_active = False
            encounter.save()
            location.msg_contents("|yCombat has ended!|n")

    def end_combat(self):
        """End combat (GM only)."""
        caller = self.caller
        location = caller.location

        # TODO: Add permission check for GM
        encounter = CombatEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if not encounter:
            caller.msg("|rNo active combat in this room!|n")
            return

        encounter.is_active = False
        encounter.save()

        for participant in encounter.participants.all():
            participant.is_active = False
            participant.save()

        location.msg_contents(
            f"|yCombat ended by {caller.name}!|n"
        )


class CmdAttack(MuxCommand):
    """
    Attack a target in combat.

    Usage:
      attack <target> [with <light|standard|heavy>] [using <weapon skill>]

    Examples:
      attack Bandit
      attack Bandit with heavy
      attack Orc with light using axes
      attack Guard with standard using blades

    Attack types:
      light    - Fast but weak (-50% damage, no recovery penalty)
      standard - Balanced attack (normal damage, -2 recovery)
      heavy    - Slow but powerful (+50% damage, -6 recovery)

    If not specified, defaults to standard attack using blades.
    """

    key = "attack"
    aliases = ["att", "hit"]
    locks = "cmd:all()"
    help_category = "Combat"

    def parse(self):
        """Parse the attack command arguments."""
        self.target_name = ""
        self.attack_type = "standard"
        self.weapon_skill = "blades"

        args = self.args.strip()
        if not args:
            return

        # Split by 'with' and 'using'
        parts = args.split(' with ')
        self.target_name = parts[0].strip()

        if len(parts) > 1:
            # Has 'with' clause
            remaining = parts[1]
            if ' using ' in remaining:
                type_part, skill_part = remaining.split(' using ', 1)
                self.attack_type = type_part.strip().lower()
                self.weapon_skill = skill_part.strip().lower()
            else:
                self.attack_type = remaining.strip().lower()
        elif ' using ' in args:
            # Has 'using' but no 'with'
            name_part, skill_part = args.split(' using ', 1)
            self.target_name = name_part.strip()
            self.weapon_skill = skill_part.strip().lower()

    def func(self):
        caller = self.caller
        location = caller.location

        if not self.target_name:
            caller.msg("Usage: attack <target> [with <light|standard|heavy>] [using <weapon skill>]")
            return

        # Validate attack type
        if self.attack_type not in ['light', 'standard', 'heavy']:
            caller.msg("|rInvalid attack type! Use: light, standard, or heavy|n")
            return

        # Get active combat
        encounter = CombatEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if not encounter:
            caller.msg("|rNo active combat! Use 'combat/start' to begin combat.|n")
            return

        # Get attacker participant
        attacker = CombatParticipant.objects.filter(
            encounter=encounter,
            character=caller,
            is_active=True
        ).first()

        if not attacker:
            caller.msg("|rYou are not in combat! Use 'combat/join' to join.|n")
            return

        # Check if it's attacker's turn
        current_participant = encounter.participants.filter(
            is_active=True
        ).order_by('initiative_order')[encounter.current_turn_index]

        if current_participant.id != attacker.id:
            caller.msg("|rIt's not your turn!|n")
            caller.msg(f"Current turn: |c{current_participant.character.name}|n")
            return

        # Find target
        target_obj = caller.search(self.target_name, location=location)
        if not target_obj:
            return

        defender = CombatParticipant.objects.filter(
            encounter=encounter,
            character=target_obj,
            is_active=True
        ).first()

        if not defender:
            caller.msg(f"|r{target_obj.name} is not in combat!|n")
            return

        # Check if target is casting and interrupt if hit
        if defender.is_casting:
            CombatEngine.interrupt_spell_cast(defender)
            location.msg_contents(
                f"|r{target_obj.name}'s spell casting was interrupted!|n"
            )

        # Process the attack
        result = CombatEngine.process_attack(
            attacker,
            defender,
            weapon_skill=self.weapon_skill,
            attack_type=self.attack_type
        )

        # Format and display results
        attack_result = result['attack_result']
        hit = attack_result['hit']

        # Build message
        msg = f"|c{caller.name}|n attacks |r{target_obj.name}|n with a |y{self.attack_type}|n {self.weapon_skill} attack!\n"
        msg += f"Attack roll: |w{attack_result['attacker_total']}|n vs Defense: |w{attack_result['defender_total']}|n\n"

        if hit:
            msg += f"|gHIT!|n\n"
            msg += f"Damage: |r{result['damage_dealt']}|n"
            if result['damage_soaked'] > 0:
                msg += f" (Soaked: |y{result['damage_soaked']}|n)"
            msg += f" = |r{result['final_damage']}|n damage dealt!\n"
            msg += f"|r{target_obj.name}|n HP: |g{defender.current_hp}|n/|g{defender.max_hp}|n"

            if defender.current_hp <= 0:
                msg += f"\n|r{target_obj.name} has been defeated!|n"
                defender.is_active = False
                defender.save()
        else:
            msg += f"|rMISS!|n"

        location.msg_contents(msg)

        # Advance turn
        self.advance_turn(encounter)

    def advance_turn(self, encounter):
        """Advance to the next turn."""
        # Advance spell casting for current participant
        current_participants = encounter.participants.filter(is_active=True).order_by('initiative_order')

        if encounter.current_turn_index < len(current_participants):
            current = current_participants[encounter.current_turn_index]
            if current.is_casting:
                status = CombatEngine.advance_spell_cast(current)
                if status['ready']:
                    encounter.location.msg_contents(
                        f"|m{current.character.name}'s spell is ready to cast!|n"
                    )

        # Move to next participant
        encounter.current_turn_index += 1
        active_count = current_participants.count()

        if encounter.current_turn_index >= active_count:
            # New round
            encounter.current_round += 1
            encounter.current_turn_index = 0
            encounter.save()

            encounter.location.msg_contents(
                f"\n|y{'=' * 70}|n\n"
                f"|yRound {encounter.current_round}|n\n"
                f"|y{'=' * 70}|n"
            )
        else:
            encounter.save()

        # Show whose turn it is
        next_participant = current_participants[encounter.current_turn_index]
        encounter.location.msg_contents(
            f"\n|g{next_participant.character.name}'s turn!|n"
        )


class CmdCast(MuxCommand):
    """
    Cast a spell at a target.

    Usage:
      cast <difficulty> <element> at <target>
      cast/complete <target>

    Switches:
      complete - Complete a spell that's been charged for 2 turns

    Difficulties:
      easy      - 10 CR, 1d10-2 damage
      moderate  - 15 CR, 2d10 damage
      difficult - 20 CR, 3d10 damage
      elite     - 20+ CR, 5d10 damage

    Elements:
      fire, ice, lightning, earth, wind, arcane

    Examples:
      cast easy fire at Bandit
      cast moderate ice at Orc
      cast/complete Guard

    Note: Spells take 2 turns to cast. If you're hit while casting,
    the spell is interrupted and lost! Sign Sorcery can only cast
    easy and moderate spells.
    """

    key = "cast"
    aliases = ["spell", "magic"]
    locks = "cmd:all()"
    help_category = "Combat"

    def parse(self):
        """Parse cast command arguments."""
        self.difficulty = ""
        self.element = ""
        self.target_name = ""
        self.complete = "complete" in self.switches

        if self.complete:
            self.target_name = self.args.strip()
            return

        args = self.args.strip()
        if not args:
            return

        # Parse: <difficulty> <element> at <target>
        if ' at ' in args:
            spell_part, self.target_name = args.split(' at ', 1)
            self.target_name = self.target_name.strip()

            parts = spell_part.strip().split()
            if len(parts) >= 2:
                self.difficulty = parts[0].lower()
                self.element = parts[1].lower()
        else:
            parts = args.split()
            if len(parts) >= 2:
                self.difficulty = parts[0].lower()
                self.element = parts[1].lower()

    def func(self):
        caller = self.caller
        location = caller.location

        # Get combat encounter
        encounter = CombatEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if not encounter:
            caller.msg("|rNo active combat!|n")
            return

        # Get caster participant
        caster = CombatParticipant.objects.filter(
            encounter=encounter,
            character=caller,
            is_active=True
        ).first()

        if not caster:
            caller.msg("|rYou are not in combat!|n")
            return

        # Check turn
        current = encounter.participants.filter(is_active=True).order_by('initiative_order')[encounter.current_turn_index]
        if current.id != caster.id:
            caller.msg("|rIt's not your turn!|n")
            return

        if self.complete:
            self.complete_spell(caster, encounter)
        else:
            self.begin_spell(caster, encounter)

    def begin_spell(self, caster, encounter):
        """Begin casting a spell."""
        if not self.difficulty or not self.element or not self.target_name:
            self.caller.msg("Usage: cast <difficulty> <element> at <target>")
            return

        # Validate difficulty
        if self.difficulty not in ['easy', 'moderate', 'difficult', 'elite']:
            self.caller.msg("|rInvalid difficulty! Use: easy, moderate, difficult, or elite|n")
            return

        # Validate element
        if self.element not in ['fire', 'ice', 'lightning', 'earth', 'wind', 'arcane']:
            self.caller.msg("|rInvalid element! Use: fire, ice, lightning, earth, wind, or arcane|n")
            return

        # Check if character has magery or sign sorcery
        has_magery = self.caller.has_skill_access('magery')
        has_signs = self.caller.has_skill_access('sign_sorcery')

        if not has_magery and not has_signs:
            self.caller.msg("|rYou don't have access to magic!|n")
            return

        spell_type = 'sign_sorcery' if has_signs and not has_magery else 'magery'

        # Begin casting
        result = CombatEngine.begin_spell_cast(
            caster,
            self.difficulty,
            self.element,
            spell_type
        )

        if not result['success']:
            self.caller.msg(f"|r{result['message']}|n")
            return

        encounter.location.msg_contents(
            f"|m{self.caller.name}|n begins casting a |y{self.difficulty}|n |c{self.element}|n spell!\n"
            f"|y{result['message']}|n"
        )

        # Store target for later
        caster.spell_element = self.element  # We'll use this to remember the target
        caster.save()

        # Advance turn
        self.advance_turn(encounter)

    def complete_spell(self, caster, encounter):
        """Complete a spell cast."""
        if not caster.is_casting:
            self.caller.msg("|rYou are not casting a spell!|n")
            return

        if caster.spell_turns_remaining > 0:
            self.caller.msg(f"|rSpell needs {caster.spell_turns_remaining} more turn(s) to cast!|n")
            return

        # Find target
        target_obj = self.caller.search(self.target_name, location=encounter.location)
        if not target_obj:
            return

        target = CombatParticipant.objects.filter(
            encounter=encounter,
            character=target_obj,
            is_active=True
        ).first()

        if not target:
            self.caller.msg(f"|r{target_obj.name} is not in combat!|n")
            return

        # Determine spell type
        has_magery = self.caller.has_skill_access('magery')
        spell_type = 'magery' if has_magery else 'sign_sorcery'

        # Complete the spell
        result = CombatEngine.complete_spell_cast(caster, target, spell_type)

        # Display results
        msg = f"|m{self.caller.name}|n unleashes |y{result['spell_name']}|n at |r{target_obj.name}|n!\n"
        msg += f"Spell roll: "

        if result['hit']:
            msg += f"|gSUCCESS!|n\n"
            msg += f"Damage: |r{result['damage_dealt']}|n (Soaked: |y{result['damage_soaked']}|n) "
            msg += f"= |r{result['final_damage']}|n damage!\n"
            msg += f"|r{target_obj.name}|n HP: |g{target.current_hp}|n/|g{target.max_hp}|n"

            if target.current_hp <= 0:
                msg += f"\n|r{target_obj.name} has been defeated!|n"
                target.is_active = False
                target.save()
        else:
            msg += f"|rFAILED!|n The spell fizzles out."

        encounter.location.msg_contents(msg)

        # Advance turn
        self.advance_turn(encounter)

    def advance_turn(self, encounter):
        """Advance to next turn."""
        current_participants = encounter.participants.filter(is_active=True).order_by('initiative_order')

        # Advance spell casting for all participants
        for participant in current_participants:
            if participant.is_casting:
                status = CombatEngine.advance_spell_cast(participant)
                if status.get('ready'):
                    encounter.location.msg_contents(
                        f"|m{participant.character.name}'s spell is ready!|n Use |wcast/complete <target>|n"
                    )

        encounter.current_turn_index += 1
        active_count = current_participants.count()

        if encounter.current_turn_index >= active_count:
            encounter.current_round += 1
            encounter.current_turn_index = 0
            encounter.save()
            encounter.location.msg_contents(f"\n|y=== Round {encounter.current_round} ===|n")
        else:
            encounter.save()

        next_participant = current_participants[encounter.current_turn_index]
        encounter.location.msg_contents(f"\n|g{next_participant.character.name}'s turn!|n")


class CmdStance(MuxCommand):
    """
    Change your combat stance.

    Usage:
      stance <defensive|moderate|offensive>

    Stances:
      defensive  - +5 Reflexes for defense, +10 CR to your attacks
      moderate   - Balanced, no bonuses or penalties
      offensive  - +5 Agility for attacks, +10 CR to defend against attacks

    Examples:
      stance defensive
      stance offensive
      stance moderate
    """

    key = "stance"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        location = caller.location

        if not self.args:
            caller.msg("Usage: stance <defensive|moderate|offensive>")
            return

        new_stance = self.args.strip().lower()

        if new_stance not in ['defensive', 'moderate', 'offensive']:
            caller.msg("|rInvalid stance! Use: defensive, moderate, or offensive|n")
            return

        # Get combat encounter
        encounter = CombatEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if not encounter:
            caller.msg("|rNo active combat!|n")
            return

        # Get participant
        participant = CombatParticipant.objects.filter(
            encounter=encounter,
            character=caller,
            is_active=True
        ).first()

        if not participant:
            caller.msg("|rYou are not in combat!|n")
            return

        # Change stance
        result = CombatEngine.change_stance(participant, new_stance)

        bonuses = result['bonuses']
        bonus_str = ""
        if new_stance == 'defensive':
            bonus_str = "(+5 Reflexes defense, +10 CR to attacks)"
        elif new_stance == 'offensive':
            bonus_str = "(+5 Agility attack, +10 CR to defense)"
        else:
            bonus_str = "(balanced)"

        location.msg_contents(
            f"|c{caller.name}|n shifts to |y{new_stance}|n stance {bonus_str}"
        )


class CmdCombatStatus(MuxCommand):
    """
    View the current combat status.

    Usage:
      combatstatus
      cs

    Shows all combatants, their HP, initiative order,
    current turn, stances, and any active effects.
    """

    key = "combatstatus"
    aliases = ["cs", "combat status"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        location = caller.location

        encounter = CombatEncounter.objects.filter(
            location=location,
            is_active=True
        ).first()

        if not encounter:
            caller.msg("|rNo active combat in this room.|n")
            return

        status = CombatEngine.format_combat_status(encounter)
        caller.msg(status)
