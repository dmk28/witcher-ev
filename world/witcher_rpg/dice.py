"""
Dice rolling system for Witcher RPG.
Uses d10 (10-sided dice) with exploding mechanics.

When a 10 is rolled, it "explodes" - you roll percentile dice (d100)
and add the result (11-100) to your total.
"""
import random
from typing import List, Tuple, Dict


class DiceRoller:
    """
    Handles all dice rolling mechanics for the Witcher RPG system.
    """

    @staticmethod
    def roll_d10() -> int:
        """
        Roll a single 10-sided die.

        Returns:
            int: Result from 1 to 10
        """
        return random.randint(1, 10)

    @staticmethod
    def roll_d100() -> int:
        """
        Roll percentile dice (d100).

        Returns:
            int: Result from 1 to 100
        """
        return random.randint(1, 100)

    @staticmethod
    def roll_exploding_d10() -> Tuple[int, bool, List[int]]:
        """
        Roll a d10 with exploding mechanics.
        If a 10 is rolled, roll d100 and add 10 more (so range becomes 11-110).

        Returns:
            tuple: (total_result, exploded, roll_details)
                - total_result: The final value
                - exploded: True if the die exploded
                - roll_details: List of individual rolls [initial_roll, explosion_roll if any]
        """
        initial_roll = DiceRoller.roll_d10()
        roll_details = [initial_roll]

        if initial_roll == 10:
            # Die explodes! Roll d100 and add 10 more
            explosion = DiceRoller.roll_d100()
            roll_details.append(explosion)
            total = 10 + explosion
            return (total, True, roll_details)
        else:
            return (initial_roll, False, roll_details)

    @staticmethod
    def roll_multiple_d10(num_dice: int) -> Dict:
        """
        Roll multiple d10s, each with explosion mechanics.

        Args:
            num_dice: Number of dice to roll

        Returns:
            dict: {
                'rolls': List of individual roll results,
                'total': Sum of all rolls,
                'explosions': Number of dice that exploded,
                'details': Detailed breakdown of each roll
            }
        """
        if num_dice <= 0:
            return {
                'rolls': [],
                'total': 0,
                'explosions': 0,
                'details': []
            }

        rolls = []
        explosions = 0
        details = []

        for i in range(num_dice):
            result, exploded, roll_details = DiceRoller.roll_exploding_d10()
            rolls.append(result)
            if exploded:
                explosions += 1
            details.append({
                'die_number': i + 1,
                'result': result,
                'exploded': exploded,
                'rolls': roll_details
            })

        return {
            'rolls': rolls,
            'total': sum(rolls),
            'explosions': explosions,
            'details': details
        }

    @staticmethod
    def format_roll_result(roll_result: Dict, include_details: bool = True) -> str:
        """
        Format a roll result for display.

        Args:
            roll_result: Result dictionary from roll_multiple_d10
            include_details: Whether to include detailed breakdown

        Returns:
            str: Formatted string describing the roll
        """
        if not roll_result['rolls']:
            return "No dice rolled"

        num_dice = len(roll_result['rolls'])
        total = roll_result['total']
        explosions = roll_result['explosions']

        output = f"**{num_dice}d10 Roll: {total}**"

        if explosions > 0:
            output += f" ({explosions} exploded!)"

        if include_details:
            output += "\n|nIndividual rolls: "
            roll_strs = []
            for detail in roll_result['details']:
                if detail['exploded']:
                    base_roll = detail['rolls'][0]
                    explosion_roll = detail['rolls'][1]
                    roll_strs.append(f"[|y{base_roll}|n->|r{explosion_roll}|n=|g{detail['result']}|n]")
                else:
                    roll_strs.append(f"[{detail['result']}]")
            output += " ".join(roll_strs)

        return output


class ChallengeResolver:
    """
    Resolves challenge checks - both fixed difficulty and contested rolls.
    """

    @staticmethod
    def fixed_difficulty_check(
        num_dice: int,
        difficulty: int,
        threshold_type: str = 'meet_or_beat'
    ) -> Dict:
        """
        Resolve a check against a fixed difficulty.

        Args:
            num_dice: Number of dice to roll (typically stat + skill + bonuses)
            difficulty: The target number to meet/beat
            threshold_type: 'meet_or_beat' (>=) or 'exceed' (>)

        Returns:
            dict: {
                'success': True/False,
                'roll_result': Full roll details,
                'margin': How much the roll exceeded/fell short,
                'difficulty': The difficulty number
            }
        """
        roll_result = DiceRoller.roll_multiple_d10(num_dice)
        total = roll_result['total']

        if threshold_type == 'meet_or_beat':
            success = total >= difficulty
        else:  # exceed
            success = total > difficulty

        margin = total - difficulty

        return {
            'success': success,
            'roll_result': roll_result,
            'margin': margin,
            'difficulty': difficulty
        }

    @staticmethod
    def contested_check(
        attacker_dice: int,
        defender_dice: int
    ) -> Dict:
        """
        Resolve a contested roll between two parties.

        Args:
            attacker_dice: Number of dice for the attacker
            defender_dice: Number of dice for the defender

        Returns:
            dict: {
                'attacker_wins': True/False,
                'attacker_roll': Full roll details,
                'defender_roll': Full roll details,
                'margin': Difference between rolls
            }
        """
        attacker_roll = DiceRoller.roll_multiple_d10(attacker_dice)
        defender_roll = DiceRoller.roll_multiple_d10(defender_dice)

        attacker_total = attacker_roll['total']
        defender_total = defender_roll['total']

        attacker_wins = attacker_total > defender_total
        margin = attacker_total - defender_total

        return {
            'attacker_wins': attacker_wins,
            'attacker_roll': attacker_roll,
            'defender_roll': defender_roll,
            'margin': margin
        }

    @staticmethod
    def format_challenge_result(challenge_result: Dict, check_type: str = 'fixed') -> str:
        """
        Format a challenge result for display.

        Args:
            challenge_result: Result from fixed_difficulty_check or contested_check
            check_type: 'fixed' or 'contested'

        Returns:
            str: Formatted string describing the result
        """
        if check_type == 'fixed':
            roll_str = DiceRoller.format_roll_result(
                challenge_result['roll_result'],
                include_details=True
            )
            success_str = "|g**SUCCESS**|n" if challenge_result['success'] else "|r**FAILURE**|n"
            margin_str = ""
            if challenge_result['margin'] > 0:
                margin_str = f" (|g+{challenge_result['margin']}|n over difficulty)"
            elif challenge_result['margin'] < 0:
                margin_str = f" (|r{challenge_result['margin']}|n under difficulty)"

            return (
                f"{roll_str}\n"
                f"|nDifficulty: {challenge_result['difficulty']}\n"
                f"|nResult: {success_str}{margin_str}"
            )
        else:  # contested
            attacker_str = DiceRoller.format_roll_result(
                challenge_result['attacker_roll'],
                include_details=False
            )
            defender_str = DiceRoller.format_roll_result(
                challenge_result['defender_roll'],
                include_details=False
            )

            winner_str = (
                "|g**ATTACKER WINS**|n"
                if challenge_result['attacker_wins']
                else "|r**DEFENDER WINS**|n"
            )
            margin_str = f"Margin: {abs(challenge_result['margin'])}"

            return (
                f"Attacker: {attacker_str}\n"
                f"|nDefender: {defender_str}\n"
                f"|n{winner_str} ({margin_str})"
            )


# Convenience functions for quick access
def roll(num_dice: int) -> Dict:
    """Quick roll of multiple d10s."""
    return DiceRoller.roll_multiple_d10(num_dice)


def check(num_dice: int, difficulty: int) -> Dict:
    """Quick fixed difficulty check."""
    return ChallengeResolver.fixed_difficulty_check(num_dice, difficulty)


def contest(attacker_dice: int, defender_dice: int) -> Dict:
    """Quick contested roll."""
    return ChallengeResolver.contested_check(attacker_dice, defender_dice)
