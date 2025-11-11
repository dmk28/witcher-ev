"""
Loot generation system for Witcher RPG.
Handles weighted tier-based loot distribution and reward calculation.
"""
import random
from .item_models import ItemTemplate, InventoryItem, Currency
from .room_models import Mission


class LootGenerator:
    """
    Generates loot based on mission danger level and tier weights.
    """

    @staticmethod
    def generate_loot_for_mission(mission, num_items=3):
        """
        Generate loot items for a completed mission.

        Args:
            mission: Mission instance
            num_items: Number of items to generate

        Returns:
            list: List of ItemTemplate instances
        """
        loot_weights = mission.loot_tier_weights
        artifact_mult = mission.artifact_multiplier

        # Apply artifact multiplier to tier_4
        if 'tier_4' in loot_weights:
            adjusted_weights = loot_weights.copy()
            adjusted_weights['tier_4'] = int(loot_weights['tier_4'] * artifact_mult)
        else:
            adjusted_weights = loot_weights

        loot_items = []
        for _ in range(num_items):
            tier = LootGenerator._weighted_tier_selection(adjusted_weights)
            item = LootGenerator._select_item_by_tier(tier)
            if item:
                loot_items.append(item)

        return loot_items

    @staticmethod
    def _weighted_tier_selection(tier_weights):
        """
        Select a tier based on weighted probabilities.

        Args:
            tier_weights: Dict like {'tier_1': 50, 'tier_2': 30, ...}

        Returns:
            str: Selected tier key
        """
        tiers = list(tier_weights.keys())
        weights = list(tier_weights.values())

        # If all weights are 0, default to tier_1
        if sum(weights) == 0:
            return 'tier_1'

        selected = random.choices(tiers, weights=weights, k=1)[0]
        return selected

    @staticmethod
    def _select_item_by_tier(tier):
        """
        Select a random item template of the given tier.

        Args:
            tier: Tier string like 'tier_1', 'tier_2', etc.

        Returns:
            ItemTemplate or None
        """
        items = ItemTemplate.objects.filter(tier=tier)
        if items.exists():
            return random.choice(items)
        return None

    @staticmethod
    def award_loot_to_character(character, loot_items):
        """
        Award loot items to a character's inventory.

        Args:
            character: ObjectDB character instance
            loot_items: List of ItemTemplate instances

        Returns:
            list: List of created InventoryItem instances
        """
        awarded = []
        for template in loot_items:
            # Check if item is stackable and already in inventory
            if template.is_stackable:
                existing = InventoryItem.objects.filter(
                    owner=character,
                    template=template,
                    is_equipped=False
                ).first()

                if existing and existing.quantity < template.max_stack:
                    # Add to existing stack
                    existing.quantity += 1
                    existing.save()
                    awarded.append(existing)
                    continue

            # Create new inventory item
            inv_item = InventoryItem.objects.create(
                template=template,
                owner=character,
                quantity=1
            )
            awarded.append(inv_item)

        return awarded

    @staticmethod
    def award_gold(character, amount):
        """
        Award gold to a character.

        Args:
            character: ObjectDB character instance
            amount: Gold amount to award

        Returns:
            Currency: Updated currency instance
        """
        currency, created = Currency.objects.get_or_create(
            character=character,
            defaults={'gold': 0}
        )

        currency.gold += amount
        currency.save()

        return currency

    @staticmethod
    def award_experience(character, amount):
        """
        Award experience to a character.

        Args:
            character: ObjectDB character instance
            amount: XP to award

        Returns:
            bool: Success
        """
        if hasattr(character, 'db_character') and character.db_character:
            char_model = character.db_character
            char_model.experience_points += amount
            char_model.save()
            return True
        return False

    @staticmethod
    def complete_mission_rewards(mission, participants, dm=None):
        """
        Award all rewards for a completed mission.

        Args:
            mission: Mission instance
            participants: List of character ObjectDB instances
            dm: DM character ObjectDB instance (gets 2 XP only)

        Returns:
            dict: Rewards distributed
        """
        rewards = {
            'participants': {},
            'dm': None
        }

        # Award DM
        if dm:
            LootGenerator.award_experience(dm, 2)
            rewards['dm'] = {'xp': 2}

        # Award each participant
        for character in participants:
            char_rewards = {
                'gold': 0,
                'xp': 0,
                'items': []
            }

            # Gold
            gold_amount = mission.base_gold_reward
            LootGenerator.award_gold(character, gold_amount)
            char_rewards['gold'] = gold_amount

            # Experience
            xp_amount = mission.experience_reward
            LootGenerator.award_experience(character, xp_amount)
            char_rewards['xp'] = xp_amount

            # Loot (3-5 items based on danger)
            num_items = {
                'safe': 1,
                'low': 2,
                'moderate': 3,
                'high': 4,
                'critical': 5
            }.get(mission.danger_level, 3)

            loot_items = LootGenerator.generate_loot_for_mission(mission, num_items)
            awarded_items = LootGenerator.award_loot_to_character(character, loot_items)
            char_rewards['items'] = [item.template.name for item in awarded_items]

            rewards['participants'][character.db_key] = char_rewards

        return rewards


class ExtractionSystem:
    """
    Handles resource extraction from extraction rooms.
    """

    @staticmethod
    def attempt_extraction(character, witcher_room, resource_name):
        """
        Attempt to extract a resource from a room.

        Args:
            character: ObjectDB character instance
            witcher_room: WitcherRoom instance
            resource_name: Name of resource to extract

        Returns:
            dict: Extraction result
        """
        from world.witcher_rpg.dice import ChallengeResolver
        from .room_models import ExtractionResource

        # Get extraction resource
        extraction_resource = ExtractionResource.objects.filter(
            biome=witcher_room.biome,
            resource_name=resource_name
        ).first()

        if not extraction_resource:
            return {
                'success': False,
                'message': f"No {resource_name} available in this {witcher_room.get_biome_display()}."
            }

        # Calculate dice pool (use appropriate stat + skill)
        # For simplicity, use Perception + Athletics
        dice_pool = character.get_stat('perception') + character.get_skill('athletics')

        # Roll vs extraction difficulty
        result = ChallengeResolver.fixed_difficulty_check(
            dice_pool,
            extraction_resource.extraction_difficulty
        )

        if not result['success']:
            # Failed extraction still increases danger
            witcher_room.increment_extraction_timer(
                extraction_resource.danger_increase_per_extraction // 2
            )

            return {
                'success': False,
                'message': f"Failed to extract {resource_name}.",
                'roll_result': result
            }

        # Success! Determine quantity
        quantity = random.randint(
            extraction_resource.base_quantity_min,
            extraction_resource.base_quantity_max
        )

        # Award items
        items_awarded = []
        for _ in range(quantity):
            inv_item = InventoryItem.objects.create(
                template=extraction_resource.item_template,
                owner=character,
                quantity=1
            )
            items_awarded.append(inv_item)

        # Increase danger timer
        became_mission = witcher_room.increment_extraction_timer(
            extraction_resource.danger_increase_per_extraction
        )

        return {
            'success': True,
            'message': f"Extracted {quantity}x {resource_name}!",
            'quantity': quantity,
            'items': items_awarded,
            'danger_increased': extraction_resource.danger_increase_per_extraction,
            'became_mission': became_mission,
            'roll_result': result
        }

    @staticmethod
    def get_available_resources(witcher_room):
        """
        Get list of extractable resources in a room.

        Args:
            witcher_room: WitcherRoom instance

        Returns:
            QuerySet: ExtractionResource instances
        """
        from .room_models import ExtractionResource

        return ExtractionResource.objects.filter(
            biome=witcher_room.biome
        )


class CraftingSystem:
    """
    Handles item crafting with tier-based difficulties and material quality.

    Crafting Difficulties by Tier:
    - Tier I: 10-20 CR (basic items)
    - Tier II: 30-50 CR (quality items)
    - Tier III: 60-85 CR (exceptional items)
    - Tier IV: 90-120 CR (relics/artifacts)

    Material Quality Reduction:
    - Tier I materials: 0-2 CR per unit
    - Tier II materials: 3-7 CR per unit
    - Tier III materials: 8-15 CR per unit
    - Tier IV materials: 20-35 CR per unit
    """

    TIER_DIFFICULTY_RANGES = {
        'tier_1': (10, 20),
        'tier_2': (30, 50),
        'tier_3': (60, 85),
        'tier_4': (90, 120),
    }

    @staticmethod
    def get_tier_info(tier):
        """Get difficulty range for a tier."""
        return CraftingSystem.TIER_DIFFICULTY_RANGES.get(tier, (10, 20))

    @staticmethod
    def can_craft(character, item_template, witcher_room):
        """
        Check if character can craft an item.

        Args:
            character: ObjectDB character instance
            item_template: ItemTemplate to craft
            witcher_room: WitcherRoom instance (workshop)

        Returns:
            dict: Result with can_craft bool, reasons, and details
        """
        reasons = []

        # Check workshop
        is_valid, workshop_reason = witcher_room.is_valid_workshop(character)
        if not is_valid:
            return {
                'can_craft': False,
                'reasons': [workshop_reason]
            }

        # Check skill access
        if item_template.crafting_skill_required:
            if not character.has_skill_access('crafting'):
                return {
                    'can_craft': False,
                    'reasons': ['You do not have access to crafting skills.']
                }

        # Check materials
        if item_template.required_materials:
            for material_name, needed_qty in item_template.required_materials.items():
                # Count items in inventory
                material_template = ItemTemplate.objects.filter(
                    name=material_name
                ).first()

                if not material_template:
                    reasons.append(f"Unknown material: {material_name}")
                    continue

                owned = InventoryItem.objects.filter(
                    owner=character,
                    template=material_template
                ).aggregate(
                    total=sum('quantity')
                )['total'] or 0

                if owned < needed_qty:
                    reasons.append(
                        f"Need {needed_qty}x {material_name} (have {owned})"
                    )

        if reasons:
            return {'can_craft': False, 'reasons': reasons}

        return {'can_craft': True, 'reasons': []}

    @staticmethod
    def calculate_material_quality_reduction(character, item_template):
        """
        Calculate difficulty reduction based on material quality.

        Args:
            character: ObjectDB character instance
            item_template: ItemTemplate being crafted

        Returns:
            tuple: (total_reduction, material_details)
        """
        if not item_template.required_materials:
            return (0, [])

        total_reduction = 0
        material_details = []

        for material_name, needed_qty in item_template.required_materials.items():
            material_template = ItemTemplate.objects.filter(
                name=material_name
            ).first()

            if not material_template:
                continue

            # Get material quality bonus
            quality_bonus = material_template.material_quality_bonus
            reduction = quality_bonus * needed_qty

            total_reduction += reduction

            material_details.append({
                'name': material_name,
                'quantity': needed_qty,
                'tier': material_template.get_tier_display(),
                'quality_bonus': quality_bonus,
                'total_reduction': reduction
            })

        return (total_reduction, material_details)

    @staticmethod
    def attempt_craft(character, item_template, witcher_room):
        """
        Attempt to craft an item with material quality calculations.

        Args:
            character: ObjectDB character instance
            item_template: ItemTemplate to craft
            witcher_room: WitcherRoom instance (workshop)

        Returns:
            dict: Craft result with details
        """
        from world.witcher_rpg.dice import ChallengeResolver

        # Check if can craft
        can_craft_check = CraftingSystem.can_craft(character, item_template, witcher_room)
        if not can_craft_check['can_craft']:
            return {
                'success': False,
                'message': 'Cannot craft this item.',
                'reasons': can_craft_check['reasons']
            }

        # Calculate material quality reduction
        material_reduction, material_details = CraftingSystem.calculate_material_quality_reduction(
            character, item_template
        )

        # Get base difficulty
        base_difficulty = item_template.crafting_difficulty

        # Apply material quality reduction
        final_difficulty = max(5, base_difficulty - material_reduction)  # Minimum 5 CR

        # Get crafting skill
        crafting_skill = character.get_skill('crafting_skill')
        intelligence = character.get_stat('intelligence')
        dice_pool = intelligence + crafting_skill

        # Roll vs modified difficulty
        result = ChallengeResolver.fixed_difficulty_check(
            dice_pool,
            final_difficulty
        )

        # Build detailed message
        difficulty_info = f"Base: {base_difficulty} CR"
        if material_reduction > 0:
            difficulty_info += f" - {material_reduction} (materials) = {final_difficulty} CR"

        if not result['success']:
            # Failed craft - materials lost
            CraftingSystem._consume_materials(character, item_template)

            return {
                'success': False,
                'message': f"Failed to craft {item_template.name}. Materials lost.",
                'roll_result': result,
                'base_difficulty': base_difficulty,
                'material_reduction': material_reduction,
                'final_difficulty': final_difficulty,
                'material_details': material_details,
                'difficulty_info': difficulty_info
            }

        # Success! Consume materials and create item
        CraftingSystem._consume_materials(character, item_template)

        crafted_item = InventoryItem.objects.create(
            template=item_template,
            owner=character,
            quantity=1
        )

        return {
            'success': True,
            'message': f"Successfully crafted {item_template.name}!",
            'item': crafted_item,
            'roll_result': result,
            'base_difficulty': base_difficulty,
            'material_reduction': material_reduction,
            'final_difficulty': final_difficulty,
            'material_details': material_details,
            'difficulty_info': difficulty_info
        }

    @staticmethod
    def _consume_materials(character, item_template):
        """
        Consume materials from character's inventory.

        Args:
            character: ObjectDB character instance
            item_template: ItemTemplate being crafted
        """
        if not item_template.required_materials:
            return

        for material_name, needed_qty in item_template.required_materials.items():
            material_template = ItemTemplate.objects.filter(
                name=material_name
            ).first()

            if not material_template:
                continue

            # Get all inventory items of this material
            materials = InventoryItem.objects.filter(
                owner=character,
                template=material_template
            ).order_by('acquired_date')

            remaining = needed_qty
            for item in materials:
                if remaining <= 0:
                    break

                if item.quantity >= remaining:
                    item.quantity -= remaining
                    if item.quantity == 0:
                        item.delete()
                    else:
                        item.save()
                    remaining = 0
                else:
                    remaining -= item.quantity
                    item.delete()
