"""
Witcher RPG Combat Engine
Handles turn-based combat with initiative, stances, attack types, and magic.
"""
from .dice import DiceRoller, ChallengeResolver
from .combat_models import CombatEncounter, CombatParticipant


class CombatEngine:
    """
    Main combat engine for managing encounters.
    """

    # Spell difficulty configurations
    SPELL_DIFFICULTIES = {
        'easy': {
            'cr': 10,
            'damage_dice': 1,
            'damage_modifier': -2,
            'soak_limit': '1d10',
            'description': 'Simple spell, quick to cast'
        },
        'moderate': {
            'cr': 15,
            'damage_dice': 2,
            'damage_modifier': 0,
            'soak_limit': '1d10',
            'description': 'Standard spell with decent power'
        },
        'difficult': {
            'cr': 20,
            'damage_dice': 3,
            'damage_modifier': 0,
            'soak_limit': '1d10',
            'description': 'Powerful spell requiring skill'
        },
        'elite': {
            'cr': 20,  # +20 to base, so actually challenging
            'damage_dice': 5,
            'damage_modifier': 0,
            'soak_limit': '1d10',
            'description': 'Devastating spell, very difficult to cast'
        }
    }

    # Sign Sorcery can only be easy and moderate
    SIGN_DIFFICULTIES = ['easy', 'moderate']

    @staticmethod
    def roll_initiative(character):
        """
        Roll initiative for a character.
        Initiative = Reflexes + Perception + 1d10
        Higher initiative goes first, but we track it inverted for ordering.

        Args:
            character: WitcherCharacter typeclass instance

        Returns:
            int: Initiative roll
        """
        reflexes = character.get_stat('reflexes')
        perception = character.get_stat('perception')

        # Roll 1d10 (non-exploding for initiative)
        init_roll = DiceRoller.roll_d10()

        total = reflexes + perception + init_roll

        return total

    @staticmethod
    def calculate_attack_roll(attacker_participant, defender_participant, weapon_skill='blades'):
        """
        Calculate an attack roll.
        Attack: Agility + Weapon Skill vs Reflexes + Weapon Skill

        Args:
            attacker_participant: CombatParticipant model instance
            defender_participant: CombatParticipant model instance
            weapon_skill: Skill to use (default 'blades')

        Returns:
            dict: Attack result with hit/miss and damage
        """
        attacker_char = attacker_participant.character
        defender_char = defender_participant.character

        # Get base stats and skills
        attacker_agility = attacker_char.get_stat('agility')
        attacker_skill = attacker_char.get_skill(weapon_skill)

        defender_reflexes = defender_char.get_stat('reflexes')
        defender_skill = defender_char.get_skill(weapon_skill)

        # Apply stance bonuses
        attacker_stance = attacker_participant.get_stance_bonuses()
        defender_stance = defender_participant.get_stance_bonuses()

        # Attacker bonuses
        agility_bonus = attacker_stance.get('agility_attack', 0)
        attack_cr_penalty = attacker_stance.get('attack_cr_modifier', 0)

        # Defender bonuses
        reflexes_bonus = defender_stance.get('reflexes_defense', 0)
        defense_cr_penalty = defender_stance.get('defense_cr_modifier', 0)

        # Apply recovery penalty from last attack
        attacker_penalty = attacker_participant.recovery_penalty

        # Calculate dice pools
        attacker_dice = attacker_agility + attacker_skill + agility_bonus + attacker_penalty
        defender_dice = defender_reflexes + defender_skill + reflexes_bonus

        # Roll contested check
        result = ChallengeResolver.contested_check(
            max(attacker_dice, 1),
            max(defender_dice, 1)
        )

        # Check if attack hits considering CR penalties
        attacker_total = result['attacker_roll']['total']
        defender_total = result['defender_roll']['total'] + defense_cr_penalty

        # Adjust for attack CR penalty
        effective_attacker_total = attacker_total - attack_cr_penalty

        hit = effective_attacker_total > defender_total
        margin = effective_attacker_total - defender_total

        return {
            'hit': hit,
            'margin': margin,
            'attacker_roll': result['attacker_roll'],
            'defender_roll': result['defender_roll'],
            'attacker_total': effective_attacker_total,
            'defender_total': defender_total
        }

    @staticmethod
    def calculate_damage(attacker_participant, weapon_skill='blades', attack_type='standard'):
        """
        Calculate damage based on attack type and stats.
        Base damage = Strength + Weapon Skill

        Args:
            attacker_participant: CombatParticipant instance
            weapon_skill: Weapon skill being used
            attack_type: 'light', 'standard', or 'heavy'

        Returns:
            int: Damage dealt
        """
        attacker_char = attacker_participant.character

        strength = attacker_char.get_stat('strength')
        skill = attacker_char.get_skill(weapon_skill)

        base_damage = strength + skill

        # Apply attack type modifier
        frame_data = {
            'light': -0.5,
            'standard': 0,
            'heavy': 0.5
        }

        modifier = frame_data.get(attack_type, 0)
        damage = int(base_damage * (1 + modifier))

        return max(damage, 1)  # Minimum 1 damage

    @staticmethod
    def calculate_soak(defender_participant, attack_cr):
        """
        Calculate damage soaked.
        Soak: Endurance + Athletics + Armor vs CR of the attack

        Args:
            defender_participant: CombatParticipant instance
            attack_cr: Challenge rating of the attack

        Returns:
            dict: Soak result with amount soaked
        """
        defender_char = defender_participant.character

        endurance = defender_char.get_stat('endurance')
        athletics = defender_char.get_skill('athletics')
        armor = defender_participant.armor_value

        dice_pool = endurance + athletics + armor

        # Roll vs attack CR
        result = ChallengeResolver.fixed_difficulty_check(
            max(dice_pool, 1),
            attack_cr
        )

        # Amount soaked is based on margin of success
        if result['success']:
            soak_amount = max(result['margin'] // 2, 1)  # Every 2 over = 1 soak
        else:
            soak_amount = 0

        return {
            'soaked': soak_amount,
            'roll_result': result,
            'success': result['success']
        }

    @staticmethod
    def update_recovery_penalty(participant, attack_type):
        """
        Update the recovery penalty based on attack type used.

        Args:
            participant: CombatParticipant instance
            attack_type: 'light', 'standard', or 'heavy'
        """
        frame_data = {
            'light': {'recovery': 10, 'malus': 0},
            'standard': {'recovery': 8, 'malus': -2},
            'heavy': {'recovery': 4, 'malus': -6}
        }

        data = frame_data.get(attack_type, frame_data['standard'])
        participant.recovery_penalty = data['malus']
        participant.last_attack_type = attack_type
        participant.save()

    @staticmethod
    def process_attack(attacker_participant, defender_participant, weapon_skill='blades', attack_type='standard'):
        """
        Process a complete attack sequence.

        Args:
            attacker_participant: CombatParticipant attacking
            defender_participant: CombatParticipant defending
            weapon_skill: Weapon skill to use
            attack_type: 'light', 'standard', or 'heavy'

        Returns:
            dict: Complete attack result
        """
        # Roll attack
        attack_result = CombatEngine.calculate_attack_roll(
            attacker_participant,
            defender_participant,
            weapon_skill
        )

        result = {
            'attack_type': attack_type,
            'weapon_skill': weapon_skill,
            'attack_result': attack_result,
            'damage_dealt': 0,
            'damage_soaked': 0,
            'final_damage': 0
        }

        if attack_result['hit']:
            # Calculate damage
            damage = CombatEngine.calculate_damage(
                attacker_participant,
                weapon_skill,
                attack_type
            )

            # Defender attempts to soak
            attack_cr = attack_result['attacker_total']
            soak_result = CombatEngine.calculate_soak(
                defender_participant,
                attack_cr
            )

            soaked = soak_result['soaked']
            damage_after_soak = max(damage - soaked, 0)

            # Apply racial damage modifier
            racial_modifier = 1.0
            if hasattr(defender_char, 'db_character') and defender_char.db_character:
                race_mods = defender_char.db_character.get_race_modifiers()
                racial_modifier = race_mods.get('damage_taken_modifier', 1.0)

            final_damage = int(damage_after_soak * racial_modifier)

            # Apply damage
            defender_participant.current_hp -= final_damage
            defender_participant.save()

            result.update({
                'damage_dealt': damage,
                'damage_soaked': soaked,
                'final_damage': final_damage,
                'soak_result': soak_result
            })

        # Update attacker's recovery penalty
        CombatEngine.update_recovery_penalty(attacker_participant, attack_type)

        return result

    @staticmethod
    def begin_spell_cast(caster_participant, spell_difficulty, spell_element, spell_type='magery'):
        """
        Begin casting a spell (takes 2 turns).

        Args:
            caster_participant: CombatParticipant casting
            spell_difficulty: 'easy', 'moderate', 'difficult', or 'elite'
            spell_element: The element of the spell
            spell_type: 'magery' or 'sign_sorcery'

        Returns:
            dict: Result of beginning the cast
        """
        # Check if Sign Sorcery is limited to easy/moderate
        if spell_type == 'sign_sorcery' and spell_difficulty not in CombatEngine.SIGN_DIFFICULTIES:
            return {
                'success': False,
                'message': 'Sign Sorcery can only cast easy and moderate spells'
            }

        # Set casting state
        caster_participant.is_casting = True
        caster_participant.spell_turns_remaining = 2
        caster_participant.spell_difficulty = spell_difficulty
        caster_participant.spell_element = spell_element
        caster_participant.spell_name = f"{spell_element.title()} {spell_type.title()}"
        caster_participant.save()

        return {
            'success': True,
            'message': f'Beginning to cast {spell_difficulty} {spell_element} spell (2 turns remaining)',
            'spell_config': CombatEngine.SPELL_DIFFICULTIES[spell_difficulty]
        }

    @staticmethod
    def interrupt_spell_cast(caster_participant):
        """
        Interrupt a spell being cast (e.g., when hit).

        Args:
            caster_participant: CombatParticipant whose spell is interrupted
        """
        if caster_participant.is_casting:
            caster_participant.is_casting = False
            caster_participant.spell_turns_remaining = 0
            caster_participant.spell_name = ''
            caster_participant.spell_difficulty = ''
            caster_participant.spell_element = ''
            caster_participant.save()
            return True
        return False

    @staticmethod
    def complete_spell_cast(caster_participant, target_participant, spell_type='magery'):
        """
        Complete a spell cast and resolve its effects.

        Args:
            caster_participant: CombatParticipant casting
            target_participant: CombatParticipant target
            spell_type: 'magery' or 'sign_sorcery'

        Returns:
            dict: Spell result
        """
        caster_char = caster_participant.character
        spell_difficulty = caster_participant.spell_difficulty
        spell_element = caster_participant.spell_element

        # Get spell configuration
        spell_config = CombatEngine.SPELL_DIFFICULTIES[spell_difficulty]

        # Calculate dice pool: Wit + Magery/Sign Sorcery
        wit = caster_char.get_stat('wit')
        magic_skill = caster_char.get_skill(spell_type)
        dice_pool = wit + magic_skill

        # Get CR (may be modified by race)
        base_cr = spell_config['cr']

        # Check for racial modifiers (Elf gets -5 CR)
        race_modifier = 0
        if hasattr(caster_char, 'db_character') and caster_char.db_character:
            race_mods = caster_char.db_character.get_race_modifiers()
            race_modifier = race_mods.get('magic_cr_modifier', 0)

        effective_cr = base_cr + race_modifier

        # Roll to hit with spell
        spell_roll = ChallengeResolver.fixed_difficulty_check(
            max(dice_pool, 1),
            effective_cr
        )

        result = {
            'spell_name': caster_participant.spell_name,
            'difficulty': spell_difficulty,
            'element': spell_element,
            'spell_roll': spell_roll,
            'hit': spell_roll['success'],
            'damage_dealt': 0,
            'damage_soaked': 0,
            'final_damage': 0
        }

        if spell_roll['success']:
            # Calculate spell damage
            damage_dice = spell_config['damage_dice']
            damage_modifier = spell_config['damage_modifier']

            damage_roll = DiceRoller.roll_multiple_d10(damage_dice)
            damage = damage_roll['total'] + damage_modifier

            # Target can only soak 1d10 from spells
            soak_roll = DiceRoller.roll_exploding_d10()
            soaked = soak_roll[0]  # First element is the total

            damage_after_soak = max(damage - soaked, 0)

            # Apply racial damage modifier
            target_char = target_participant.character
            racial_modifier = 1.0
            if hasattr(target_char, 'db_character') and target_char.db_character:
                race_mods = target_char.db_character.get_race_modifiers()
                racial_modifier = race_mods.get('damage_taken_modifier', 1.0)

            final_damage = int(damage_after_soak * racial_modifier)

            # Apply damage
            target_participant.current_hp -= final_damage
            target_participant.save()

            result.update({
                'damage_roll': damage_roll,
                'damage_dealt': damage,
                'soak_roll': soak_roll,
                'damage_soaked': soaked,
                'final_damage': final_damage
            })

        # Clear casting state
        caster_participant.is_casting = False
        caster_participant.spell_turns_remaining = 0
        caster_participant.spell_name = ''
        caster_participant.save()

        return result

    @staticmethod
    def advance_spell_cast(caster_participant):
        """
        Advance spell casting by one turn.

        Args:
            caster_participant: CombatParticipant casting

        Returns:
            dict: Status of spell casting
        """
        if not caster_participant.is_casting:
            return {'casting': False}

        caster_participant.spell_turns_remaining -= 1
        caster_participant.save()

        return {
            'casting': True,
            'turns_remaining': caster_participant.spell_turns_remaining,
            'spell_name': caster_participant.spell_name,
            'ready': caster_participant.spell_turns_remaining == 0
        }

    @staticmethod
    def change_stance(participant, new_stance):
        """
        Change combat stance.

        Args:
            participant: CombatParticipant instance
            new_stance: 'defensive', 'moderate', or 'offensive'

        Returns:
            dict: Result of stance change
        """
        old_stance = participant.stance
        participant.stance = new_stance
        participant.save()

        bonuses = participant.get_stance_bonuses()

        return {
            'success': True,
            'old_stance': old_stance,
            'new_stance': new_stance,
            'bonuses': bonuses
        }

    @staticmethod
    def format_combat_status(encounter):
        """
        Format the current combat status for display.

        Args:
            encounter: CombatEncounter instance

        Returns:
            str: Formatted combat status
        """
        lines = []
        lines.append(f"|y{'=' * 70}|n")
        lines.append(f"|w{encounter.name.center(70)}|n")
        lines.append(f"|yRound {encounter.current_round}|n")
        lines.append(f"|y{'=' * 70}|n\n")

        participants = encounter.participants.filter(is_active=True).order_by('initiative_order')

        for i, p in enumerate(participants):
            is_current = (i == encounter.current_turn_index)
            marker = "|g>>> |n" if is_current else "    "

            name = p.character.name
            hp_bar = CombatEngine._create_hp_bar(p.current_hp, p.max_hp)
            stance_color = {
                'defensive': '|b',
                'moderate': '|w',
                'offensive': '|r'
            }.get(p.stance, '|w')

            status = f"{marker}|c{name}|n {hp_bar} {stance_color}{p.stance.title()}|n"

            if p.recovery_penalty < 0:
                status += f" |r(Recovery: {p.recovery_penalty})|n"

            if p.is_casting:
                status += f" |m(Casting {p.spell_name}: {p.spell_turns_remaining} turns)|n"

            lines.append(status)

        lines.append(f"\n|y{'=' * 70}|n")
        return "\n".join(lines)

    @staticmethod
    def _create_hp_bar(current_hp, max_hp, width=20):
        """Create a visual HP bar."""
        if max_hp <= 0:
            return "[|rDEAD|n]"

        percent = current_hp / max_hp
        filled = int(percent * width)
        empty = width - filled

        # Color based on HP
        if percent > 0.6:
            color = '|g'
        elif percent > 0.3:
            color = '|y'
        else:
            color = '|r'

        bar = f"[{color}{'█' * filled}|x{'░' * empty}|n] {current_hp}/{max_hp}"
        return bar
