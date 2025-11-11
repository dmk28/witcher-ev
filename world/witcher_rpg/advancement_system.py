"""
Character Advancement System for Witcher RPG

Handles XP spending, stat/skill improvements, and GM approval workflow.
"""

from world.witcher_rpg.advancement_models import AdvancementLog, ApprovalRequest
from world.witcher_rpg.models import WitcherCharacter, CharacterStats, CharacterSkills
from django.utils import timezone


class AdvancementCalculator:
    """
    Calculates XP costs for stat and skill advancements.
    """

    @staticmethod
    def calculate_stat_cost(new_rating):
        """
        Calculate XP cost for advancing a stat to the new rating.

        Formula:
        - Levels 1-5: New Rating × 10 XP
        - Levels 6-7: New Rating × 20 XP

        Args:
            new_rating: The target rating (1-7)

        Returns:
            int: XP cost
        """
        if new_rating <= 5:
            return new_rating * 10
        else:
            return new_rating * 20

    @staticmethod
    def calculate_skill_cost(new_rating, vocation=None, skill_name=None):
        """
        Calculate XP cost for advancing a skill to the new rating.

        Formula:
        - Levels 1-5: New Rating × 5 XP
        - Levels 6-7: New Rating × 15 XP

        Modified by vocation multiplier (crafters pay less for crafting, etc)

        Args:
            new_rating: The target rating (1-10)
            vocation: Character's vocation (for multiplier)
            skill_name: Name of skill (for multiplier)

        Returns:
            int: XP cost
        """
        if new_rating <= 5:
            base_cost = new_rating * 5
        else:
            base_cost = new_rating * 15

        # Apply vocation multiplier if provided
        if vocation and skill_name:
            from world.witcher_rpg.crafting_models import VocationSkillCostMultiplier
            multiplier = VocationSkillCostMultiplier.get_multiplier(vocation, skill_name)
            base_cost = int(base_cost * multiplier)

        return base_cost

    @staticmethod
    def requires_approval(new_rating):
        """
        Check if a rating requires GM approval.

        Args:
            new_rating: The target rating

        Returns:
            bool: True if GM approval is required (6-7)
        """
        return new_rating >= 6


class AdvancementManager:
    """
    Manages character advancements and approval workflow.
    """

    # Valid stat names
    STAT_NAMES = [
        'strength', 'agility', 'endurance', 'reflexes',
        'wit', 'intelligence', 'willpower', 'perception',
        'charm', 'appearance', 'graces', 'cunning'
    ]

    # Valid skill names
    SKILL_NAMES = [
        'blades', 'axes', 'maces', 'spears', 'crossbows', 'brawling',
        'alchemy', 'magery', 'sign_sorcery',
        'crafting_skill',
        'athletics', 'resistance', 'leadership', 'tactics'
    ]

    @staticmethod
    def advance_stat(character, stat_name, gm_approver=None):
        """
        Advance a character's stat by one level.

        Args:
            character: Character object
            stat_name: Name of the stat to advance
            gm_approver: GM who approved (if required)

        Returns:
            dict: Result with success, message, and details
        """
        # Validate stat name
        stat_name = stat_name.lower()
        if stat_name not in AdvancementManager.STAT_NAMES:
            return {
                'success': False,
                'message': f"Invalid stat name: {stat_name}"
            }

        # Get character data
        db_char = character.db_character
        if not db_char or not db_char.stats:
            return {
                'success': False,
                'message': "Character has no stat data."
            }

        # Get current value
        current_value = getattr(db_char.stats, stat_name, 0)

        # Check if already at maximum
        if current_value >= 7:
            return {
                'success': False,
                'message': f"{stat_name.title()} is already at maximum (7)."
            }

        new_value = current_value + 1

        # Calculate XP cost
        xp_cost = AdvancementCalculator.calculate_stat_cost(new_value)

        # Check if approval is required
        needs_approval = AdvancementCalculator.requires_approval(new_value)

        if needs_approval and not gm_approver:
            return {
                'success': False,
                'message': f"GM approval required for {stat_name.title()} level {new_value}.",
                'needs_approval': True,
                'xp_cost': xp_cost,
                'current_value': current_value,
                'target_value': new_value
            }

        # Check XP
        if db_char.experience_points < xp_cost:
            return {
                'success': False,
                'message': f"Insufficient XP. Need {xp_cost}, have {db_char.experience_points}."
            }

        # Apply advancement
        setattr(db_char.stats, stat_name, new_value)
        db_char.stats.save()

        # Deduct XP
        db_char.experience_points -= xp_cost
        db_char.save()

        # Log advancement
        AdvancementLog.objects.create(
            character=character,
            advancement_type='stat',
            stat_or_skill_name=stat_name,
            old_value=current_value,
            new_value=new_value,
            xp_cost=xp_cost,
            required_approval=needs_approval,
            approved_by=gm_approver
        )

        return {
            'success': True,
            'stat': stat_name,
            'old_value': current_value,
            'new_value': new_value,
            'xp_cost': xp_cost,
            'remaining_xp': db_char.experience_points,
            'approved_by': gm_approver.name if gm_approver else None
        }

    @staticmethod
    def advance_skill(character, skill_name, gm_approver=None):
        """
        Advance a character's skill by one level.

        Args:
            character: Character object
            skill_name: Name of the skill to advance
            gm_approver: GM who approved (if required)

        Returns:
            dict: Result with success, message, and details
        """
        # Validate skill name
        skill_name = skill_name.lower()
        if skill_name not in AdvancementManager.SKILL_NAMES:
            return {
                'success': False,
                'message': f"Invalid skill name: {skill_name}"
            }

        # Get character data
        db_char = character.db_character
        if not db_char or not db_char.skills:
            return {
                'success': False,
                'message': "Character has no skill data."
            }

        # Get current value
        current_value = getattr(db_char.skills, skill_name, 0)

        # Check if already at maximum
        if current_value >= 10:
            return {
                'success': False,
                'message': f"{skill_name.title()} is already at maximum (10)."
            }

        new_value = current_value + 1

        # Calculate XP cost (with vocation multiplier)
        xp_cost = AdvancementCalculator.calculate_skill_cost(
            new_value,
            vocation=db_char.vocation,
            skill_name=skill_name
        )

        # Check if approval is required
        needs_approval = AdvancementCalculator.requires_approval(new_value)

        if needs_approval and not gm_approver:
            return {
                'success': False,
                'message': f"GM approval required for {skill_name.title()} level {new_value}.",
                'needs_approval': True,
                'xp_cost': xp_cost,
                'current_value': current_value,
                'target_value': new_value
            }

        # Check XP
        if db_char.experience_points < xp_cost:
            return {
                'success': False,
                'message': f"Insufficient XP. Need {xp_cost}, have {db_char.experience_points}."
            }

        # Apply advancement
        setattr(db_char.skills, skill_name, new_value)
        db_char.skills.save()

        # Deduct XP
        db_char.experience_points -= xp_cost
        db_char.save()

        # Log advancement
        AdvancementLog.objects.create(
            character=character,
            advancement_type='skill',
            stat_or_skill_name=skill_name,
            old_value=current_value,
            new_value=new_value,
            xp_cost=xp_cost,
            required_approval=needs_approval,
            approved_by=gm_approver
        )

        return {
            'success': True,
            'skill': skill_name,
            'old_value': current_value,
            'new_value': new_value,
            'xp_cost': xp_cost,
            'remaining_xp': db_char.experience_points,
            'approved_by': gm_approver.name if gm_approver else None
        }

    @staticmethod
    def create_approval_request(character, advancement_type, stat_or_skill_name, justification=""):
        """
        Create a GM approval request for high-level advancement (6-7).

        Args:
            character: Character object
            advancement_type: 'stat' or 'skill'
            stat_or_skill_name: Name of stat/skill
            justification: Player's reasoning

        Returns:
            dict: Result with success, message, and request details
        """
        # Validate type and name
        stat_or_skill_name = stat_or_skill_name.lower()

        if advancement_type == 'stat':
            if stat_or_skill_name not in AdvancementManager.STAT_NAMES:
                return {
                    'success': False,
                    'message': f"Invalid stat name: {stat_or_skill_name}"
                }
        elif advancement_type == 'skill':
            if stat_or_skill_name not in AdvancementManager.SKILL_NAMES:
                return {
                    'success': False,
                    'message': f"Invalid skill name: {stat_or_skill_name}"
                }
        else:
            return {
                'success': False,
                'message': "Invalid advancement type. Must be 'stat' or 'skill'."
            }

        # Get character data
        db_char = character.db_character
        if not db_char:
            return {
                'success': False,
                'message': "Character has no data."
            }

        # Get current value
        if advancement_type == 'stat':
            current_value = getattr(db_char.stats, stat_or_skill_name, 0)
            xp_cost = AdvancementCalculator.calculate_stat_cost(current_value + 1)
        else:
            current_value = getattr(db_char.skills, stat_or_skill_name, 0)
            xp_cost = AdvancementCalculator.calculate_skill_cost(
                current_value + 1,
                vocation=db_char.vocation,
                skill_name=stat_or_skill_name
            )

        target_value = current_value + 1

        # Check if already at 7 or above
        if advancement_type == 'stat' and current_value >= 7:
            return {
                'success': False,
                'message': f"{stat_or_skill_name.title()} is already at maximum (7)."
            }

        if advancement_type == 'skill' and current_value >= 10:
            return {
                'success': False,
                'message': f"{stat_or_skill_name.title()} is already at maximum (10)."
            }

        # Check if target requires approval
        if target_value < 6:
            return {
                'success': False,
                'message': f"Levels below 6 don't require approval. Use 'advance' directly."
            }

        # Check for existing pending request
        existing = ApprovalRequest.objects.filter(
            character=character,
            stat_or_skill_name=stat_or_skill_name,
            status='pending'
        ).first()

        if existing:
            return {
                'success': False,
                'message': f"You already have a pending request for {stat_or_skill_name.title()}."
            }

        # Check XP
        if db_char.experience_points < xp_cost:
            return {
                'success': False,
                'message': f"Insufficient XP. Need {xp_cost}, have {db_char.experience_points}."
            }

        # Create request
        request = ApprovalRequest.objects.create(
            character=character,
            advancement_type=advancement_type,
            stat_or_skill_name=stat_or_skill_name,
            current_value=current_value,
            target_value=target_value,
            xp_cost=xp_cost,
            justification=justification,
            status='pending'
        )

        return {
            'success': True,
            'request_id': request.id,
            'stat_or_skill': stat_or_skill_name,
            'current_value': current_value,
            'target_value': target_value,
            'xp_cost': xp_cost,
            'message': (f"Approval request submitted for {stat_or_skill_name.title()} "
                       f"{current_value}→{target_value}.")
        }

    @staticmethod
    def process_approval(request_id, gm, approve, notes=""):
        """
        Process a GM approval request.

        Args:
            request_id: ID of the ApprovalRequest
            gm: GM character object
            approve: True to approve, False to deny
            notes: GM's notes

        Returns:
            dict: Result with success and message
        """
        try:
            request = ApprovalRequest.objects.get(id=request_id, status='pending')
        except ApprovalRequest.DoesNotExist:
            return {
                'success': False,
                'message': f"No pending approval request with ID {request_id}."
            }

        character = request.character

        if approve:
            # Approve and apply advancement
            advancement_type = request.advancement_type
            stat_or_skill_name = request.stat_or_skill_name

            if advancement_type == 'stat':
                result = AdvancementManager.advance_stat(
                    character, stat_or_skill_name, gm_approver=gm
                )
            else:
                result = AdvancementManager.advance_skill(
                    character, stat_or_skill_name, gm_approver=gm
                )

            if result['success']:
                request.status = 'approved'
                request.reviewed_by = gm
                request.review_notes = notes
                request.reviewed_at = timezone.now()
                request.save()

                return {
                    'success': True,
                    'approved': True,
                    'character': character.name,
                    'advancement': f"{stat_or_skill_name} {request.current_value}→{request.target_value}",
                    'xp_cost': request.xp_cost
                }
            else:
                return result

        else:
            # Deny request
            request.status = 'denied'
            request.reviewed_by = gm
            request.review_notes = notes
            request.reviewed_at = timezone.now()
            request.save()

            return {
                'success': True,
                'approved': False,
                'character': character.name,
                'advancement': f"{request.stat_or_skill_name} {request.current_value}→{request.target_value}",
                'message': f"Request denied by {gm.name}."
            }

    @staticmethod
    def get_advancement_cost_preview(character):
        """
        Get a preview of XP costs for all possible advancements.

        Args:
            character: Character object

        Returns:
            dict: Preview of costs for stats and skills
        """
        db_char = character.db_character
        if not db_char:
            return None

        preview = {
            'xp_available': db_char.experience_points,
            'stats': {},
            'skills': {}
        }

        # Stats
        for stat_name in AdvancementManager.STAT_NAMES:
            current = getattr(db_char.stats, stat_name, 0)
            if current < 7:
                next_value = current + 1
                cost = AdvancementCalculator.calculate_stat_cost(next_value)
                needs_approval = AdvancementCalculator.requires_approval(next_value)

                preview['stats'][stat_name] = {
                    'current': current,
                    'next': next_value,
                    'cost': cost,
                    'needs_approval': needs_approval,
                    'can_afford': db_char.experience_points >= cost
                }

        # Skills
        for skill_name in AdvancementManager.SKILL_NAMES:
            current = getattr(db_char.skills, skill_name, 0)
            if current < 10:
                next_value = current + 1
                cost = AdvancementCalculator.calculate_skill_cost(
                    next_value,
                    vocation=db_char.vocation,
                    skill_name=skill_name
                )
                needs_approval = AdvancementCalculator.requires_approval(next_value)

                # Get multiplier for display
                from world.witcher_rpg.crafting_models import VocationSkillCostMultiplier
                multiplier = VocationSkillCostMultiplier.get_multiplier(db_char.vocation, skill_name)

                preview['skills'][skill_name] = {
                    'current': current,
                    'next': next_value,
                    'cost': cost,
                    'multiplier': multiplier,
                    'needs_approval': needs_approval,
                    'can_afford': db_char.experience_points >= cost
                }

        return preview
