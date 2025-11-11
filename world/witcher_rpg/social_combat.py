"""
Social Combat System for Witcher RPG

Handles the mechanics of intrigue and social combat where characters
use social stats (Charm, Cunning, Appearance, Graces) to defeat opponents
and gain material rewards.

This system allows for:
- Seduction (like Dandelion's patronesses)
- Negotiation (merchant deals)
- Intimidation (extracting information)
- Manipulation (gaining favors and secrets)
"""

from world.witcher_rpg.dice import DiceRoller, ChallengeResolver


class SocialCombatResolver:
    """
    Handles resolution of social combat encounters.
    """

    @staticmethod
    def calculate_social_capital(character):
        """
        Calculate max social capital for a character.

        Base: (Charm + Cunning + Appearance + Graces) × 5
        Modified by social rank (higher rank = more capital)
        """
        db_char = character.db_character
        if not db_char:
            return 50  # Default for NPCs without full stats

        # Get social stats
        charm = db_char.get_total_effective_stat('charm')
        cunning = db_char.get_total_effective_stat('cunning')
        appearance = db_char.get_total_effective_stat('appearance')
        graces = db_char.get_total_effective_stat('graces')

        base_capital = (charm + cunning + appearance + graces) * 5

        # Social rank multiplier (outcasts have less, nobility has more)
        rank_multipliers = {
            1: 0.8,   # Outcast
            2: 1.0,   # Commoner
            3: 1.2,   # Knight
            4: 1.5,   # Landed Gentry
            5: 2.0,   # Royalty
        }

        social_rank = getattr(db_char, 'social_rank', 2)
        multiplier = rank_multipliers.get(social_rank, 1.0)

        return int(base_capital * multiplier)

    @staticmethod
    def roll_initiative(character):
        """
        Roll initiative for social combat.
        Uses Wit + Perception (mental quickness).
        """
        db_char = character.db_character
        if not db_char:
            return DiceRoller.roll_d10()

        wit = db_char.get_total_effective_stat('wit')
        perception = db_char.get_total_effective_stat('perception')

        dice_pool = wit + perception
        result = DiceRoller.roll_multiple_d10(max(dice_pool, 1))

        return result['total']

    @staticmethod
    def perform_social_action(actor_participant, target_participant, action, encounter):
        """
        Perform a social action (charm, undermine, etc.).

        Args:
            actor_participant: SocialParticipant performing the action
            target_participant: SocialParticipant being targeted
            action: SocialAction being performed
            encounter: SocialEncounter context

        Returns:
            dict: Result with success, damage, message
        """
        actor = actor_participant.character
        target = target_participant.character

        # Get actor's character data
        actor_db = actor.db_character
        if not actor_db:
            return {
                'success': False,
                'message': f"{actor.name} has no character data."
            }

        # Calculate dice pool
        primary_stat = actor_db.get_total_effective_stat(action.primary_stat)
        dice_pool = primary_stat

        # Add secondary stat if present
        if action.secondary_stat and action.secondary_stat != 'none':
            secondary_stat = actor_db.get_total_effective_stat(action.secondary_stat)
            dice_pool += secondary_stat

        # Stance bonuses
        stance_bonuses = SocialCombatResolver._get_stance_bonuses(
            actor_participant.stance,
            action.primary_stat
        )
        dice_pool += stance_bonuses.get('bonus_dice', 0)

        # Calculate difficulty
        difficulty = action.base_difficulty

        # Target's defensive stat (opposite of attacker's approach)
        defensive_stat = SocialCombatResolver._get_defensive_stat(action.primary_stat)
        if target.db_character:
            target_defense = target.db_character.get_total_effective_stat(defensive_stat)
            difficulty += target_defense // 2  # Defense adds to difficulty

        # Apply social rank modifier (higher rank = easier to influence lower rank)
        if actor_db and target.db_character:
            actor_rank = getattr(actor_db, 'social_rank', 2)
            target_rank = getattr(target.db_character, 'social_rank', 2)
            rank_difference = actor_rank - target_rank

            # Each rank difference modifies CR by 5
            difficulty -= (rank_difference * 5)

        difficulty = max(difficulty, 5)  # Minimum CR of 5

        # Perform the roll
        result = ChallengeResolver.fixed_difficulty_check(max(dice_pool, 1), difficulty)

        # Build result message
        response = {
            'success': result['success'],
            'roll': result,
            'dice_pool': dice_pool,
            'difficulty': difficulty,
            'damage': 0,
            'message': ''
        }

        if result['success']:
            # Calculate damage for attack actions
            if action.action_type == 'attack' and action.damage_dice > 0:
                damage_result = DiceRoller.roll_multiple_d10(action.damage_dice)
                damage = damage_result['total']

                # Add margin of success as bonus damage
                damage += max(result['margin'] // 5, 0)

                # Apply damage
                actual_damage = target_participant.take_social_damage(damage)
                actor_participant.total_damage_dealt += actual_damage
                actor_participant.save()

                response['damage'] = actual_damage
                response['damage_roll'] = damage_result

                # Check if target is defeated
                if target_participant.current_social_capital <= 0:
                    response['defeated'] = True
                    victory_margin = actor_participant.current_social_capital
                    rewards = target_participant.calculate_reward_value(victory_margin)
                    response['rewards'] = rewards

            # Handle support actions
            elif action.action_type == 'support':
                heal_amount = result['margin'] // 2 + 5
                actual_heal = target_participant.restore_social_capital(heal_amount)
                response['heal'] = actual_heal

            # Handle undermine actions (apply ongoing penalties)
            elif action.action_type == 'undermine':
                response['penalty_applied'] = action.bonus_effects
                # This would be tracked in a separate StatusEffect system

            # Handle boost actions
            elif action.action_type == 'boost':
                response['bonus_applied'] = action.bonus_effects

        return response

    @staticmethod
    def _get_stance_bonuses(stance, stat_used):
        """
        Get bonuses based on current stance and stat being used.

        Returns:
            dict: Bonuses like {'bonus_dice': 2, 'cr_modifier': -5}
        """
        bonuses = {'bonus_dice': 0, 'cr_modifier': 0}

        stance_stat_bonuses = {
            'charming': {
                'charm': {'bonus_dice': 2},
                'appearance': {'bonus_dice': 1},
            },
            'cunning': {
                'cunning': {'bonus_dice': 2},
                'graces': {'bonus_dice': 1},
            },
            'bold': {
                'charm': {'bonus_dice': 1},
                'cunning': {'cr_modifier': -5},
            },
            'subtle': {
                'graces': {'bonus_dice': 2},
                'cunning': {'bonus_dice': 1},
            },
        }

        stance_bonuses = stance_stat_bonuses.get(stance, {}).get(stat_used, {})
        bonuses.update(stance_bonuses)

        return bonuses

    @staticmethod
    def _get_defensive_stat(attacking_stat):
        """
        Get the defensive stat that opposes an attacking stat.

        Charm vs Cunning (see through charm with wit)
        Cunning vs Graces (grace deflects manipulation)
        Appearance vs Graces (social grace resists appearance)
        Graces vs Charm (charm overcomes formality)
        """
        defense_map = {
            'charm': 'cunning',
            'cunning': 'graces',
            'appearance': 'graces',
            'graces': 'charm',
        }

        return defense_map.get(attacking_stat, 'cunning')

    @staticmethod
    def format_social_action_result(actor, target, action, result):
        """
        Format the result of a social action into a readable message.

        Args:
            actor: Character performing the action
            target: Character being targeted
            action: SocialAction performed
            result: Result dict from perform_social_action

        Returns:
            str: Formatted message
        """
        lines = []

        # Header
        lines.append(f"|c{actor.name}|n uses |y{action.name}|n on |c{target.name}|n!")

        # Roll result
        roll_msg = ChallengeResolver.format_challenge_result(result['roll'], 'fixed')
        lines.append(f"  Roll: {result['dice_pool']}d10 vs CR {result['difficulty']}")
        lines.append(f"  {roll_msg}")

        if result['success']:
            if result.get('damage', 0) > 0:
                lines.append(
                    f"  |r{target.name} loses {result['damage']} social capital!|n"
                )

                if result.get('defeated'):
                    lines.append(f"\n|y{target.name} is socially defeated!|n")

                    # Show rewards
                    rewards = result.get('rewards', {})
                    if rewards.get('gold', 0) > 0:
                        lines.append(f"|gReward: {rewards['gold']} crowns!|n")
                    if rewards.get('item_tier'):
                        lines.append(f"|gBonus: Gained a {rewards['item_tier']} item!|n")
                    if rewards.get('favor_level', 0) > 0:
                        lines.append(f"|gFavor: Level {rewards['favor_level']} favor owed!|n")

            elif result.get('heal', 0) > 0:
                lines.append(
                    f"  |g{target.name} regains {result['heal']} social capital!|n"
                )

            elif result.get('penalty_applied'):
                lines.append(f"  |yPenalty applied to {target.name}!|n")

            elif result.get('bonus_applied'):
                lines.append(f"  |gBonus applied to {target.name}!|n")
        else:
            lines.append(f"  |rThe action fails to have an effect.|n")

        return "\n".join(lines)


class SocialEncounterManager:
    """
    Manages social encounters (creating, updating, ending).
    """

    @staticmethod
    def create_encounter(location, encounter_type='negotiation', name=None, stakes=None):
        """
        Create a new social encounter.

        Args:
            location: ObjectDB where encounter takes place
            encounter_type: Type of social encounter
            name: Optional name for the encounter
            stakes: Optional dict of what's at stake

        Returns:
            SocialEncounter: The created encounter
        """
        from world.witcher_rpg.social_models import SocialEncounter

        if not name:
            name = f"{encounter_type.title()} at {location.name}"

        encounter = SocialEncounter.objects.create(
            name=name,
            location=location,
            encounter_type=encounter_type,
            stakes=stakes or {}
        )

        return encounter

    @staticmethod
    def add_participant(encounter, character, wealth_level=2):
        """
        Add a character to a social encounter.

        Args:
            encounter: SocialEncounter
            character: Character object (Evennia ObjectDB)
            wealth_level: Character's wealth level (1-7)

        Returns:
            SocialParticipant: The created participant
        """
        from world.witcher_rpg.social_models import SocialParticipant

        # Calculate social capital
        max_capital = SocialCombatResolver.calculate_social_capital(character)

        # Roll initiative
        initiative = SocialCombatResolver.roll_initiative(character)

        # Create participant
        participant = SocialParticipant.objects.create(
            encounter=encounter,
            character=character,
            initiative_roll=initiative,
            current_social_capital=max_capital,
            max_social_capital=max_capital,
            wealth_level=wealth_level
        )

        # Determine initiative order
        SocialEncounterManager._update_initiative_order(encounter)

        return participant

    @staticmethod
    def _update_initiative_order(encounter):
        """
        Update initiative order for all participants.
        Higher initiative rolls go first.
        """
        participants = encounter.participants.all().order_by('-initiative_roll', 'id')

        for index, participant in enumerate(participants):
            participant.initiative_order = index
            participant.save()

    @staticmethod
    def end_encounter(encounter, winner=None):
        """
        End a social encounter and distribute rewards.

        Args:
            encounter: SocialEncounter to end
            winner: Optional winning participant

        Returns:
            dict: Summary of encounter results
        """
        encounter.is_active = False
        encounter.save()

        # Get all defeated participants
        defeated = encounter.participants.filter(is_active=False)

        results = {
            'winner': winner.character.name if winner else None,
            'defeated': [p.character.name for p in defeated],
            'rewards': []
        }

        # Calculate rewards for winner from defeated opponents
        if winner:
            for defeated_participant in defeated:
                victory_margin = winner.current_social_capital
                rewards = defeated_participant.calculate_reward_value(victory_margin)

                results['rewards'].append({
                    'from': defeated_participant.character.name,
                    'gold': rewards['gold'],
                    'item_tier': rewards.get('item_tier'),
                    'favor_level': rewards.get('favor_level', 0)
                })

        return results

    @staticmethod
    def get_available_actions(participant, encounter):
        """
        Get list of actions available to a participant given their stance
        and the encounter type.

        Returns:
            QuerySet: Available SocialAction objects
        """
        from world.witcher_rpg.social_models import SocialAction

        all_actions = SocialAction.objects.all()

        available = []
        for action in all_actions:
            if action.can_use_in_encounter(encounter.encounter_type, participant.stance):
                available.append(action)

        return available
