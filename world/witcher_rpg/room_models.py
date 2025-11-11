"""
Room and Mission system models for Witcher RPG.
Includes three room types: Adventure, Bank/Storage, and Extraction.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB


class RoomType(models.TextChoices):
    """Types of rooms in the game."""
    ADVENTURE = 'adventure', 'Outdoor/Adventure Room'
    BANK = 'bank', 'Bank/Storage Room'
    EXTRACTION = 'extraction', 'Extraction/Resource Room'


class BiomeType(models.TextChoices):
    """Biome types for extraction and adventure rooms."""
    FOREST = 'forest', 'Forest'
    MINE = 'mine', 'Mine'
    HILLS = 'hills', 'Hills'
    RIVER = 'river', 'River'
    OCEAN = 'ocean', 'Ocean'
    PLAINS = 'plains', 'Plains'
    MOUNTAINS = 'mountains', 'Mountains'
    SWAMP = 'swamp', 'Swamp'
    DESERT = 'desert', 'Desert'
    URBAN = 'urban', 'Urban/City'


class DangerLevel(models.TextChoices):
    """Danger levels for rooms and missions."""
    SAFE = 'safe', 'Safe'
    LOW = 'low', 'Low Danger'
    MODERATE = 'moderate', 'Moderate Danger'
    HIGH = 'high', 'High Danger'
    CRITICAL = 'critical', 'Critical Danger'


class WitcherRoom(models.Model):
    """
    Extended room information for the Witcher RPG system.
    Links to an Evennia room object.
    """
    room_object = models.OneToOneField(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='witcher_room',
        help_text="The Evennia room object"
    )

    room_type = models.CharField(
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.ADVENTURE,
        help_text="Type of room"
    )

    biome = models.CharField(
        max_length=20,
        choices=BiomeType.choices,
        default=BiomeType.PLAINS,
        help_text="Biome type (for extraction and adventure rooms)"
    )

    danger_level = models.CharField(
        max_length=20,
        choices=DangerLevel.choices,
        default=DangerLevel.SAFE,
        help_text="Current danger level"
    )

    # For extraction rooms
    extraction_timer = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Timer for extraction rooms (0-100). At 100, becomes plot room."
    )

    # Available resources for extraction
    available_resources = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON dict of available resources: {'wood': 50, 'iron_ore': 30}"
    )

    # Mission/Plot room status
    is_mission_active = models.BooleanField(
        default=False,
        help_text="Is there an active mission in this room?"
    )

    # Organization ownership (for bank/storage rooms)
    organization = models.CharField(
        max_length=100,
        blank=True,
        help_text="Organization that owns this room (for bank/storage)"
    )

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Witcher Room"
        verbose_name_plural = "Witcher Rooms"

    def __str__(self):
        return f"{self.room_object.db_key} ({self.get_room_type_display()})"

    def increment_extraction_timer(self, amount=1):
        """Increment the extraction timer."""
        self.extraction_timer = min(self.extraction_timer + amount, 100)
        self.save()

        if self.extraction_timer >= 100:
            # Convert to mission room
            self.is_mission_active = True
            self.danger_level = DangerLevel.MODERATE
            self.save()
            return True  # Became mission room
        return False

    def get_resource_list(self):
        """Get formatted list of available resources."""
        if not self.available_resources:
            return []
        return [(name, amount) for name, amount in self.available_resources.items()]


class Mission(models.Model):
    """
    A mission/plot event that occurs in a room.
    """
    room = models.ForeignKey(
        WitcherRoom,
        on_delete=models.CASCADE,
        related_name='missions',
        help_text="Room where mission takes place"
    )

    name = models.CharField(
        max_length=200,
        help_text="Mission name"
    )

    description = models.TextField(
        help_text="Mission description and objectives"
    )

    danger_level = models.CharField(
        max_length=20,
        choices=DangerLevel.choices,
        default=DangerLevel.LOW,
        help_text="Mission danger level"
    )

    # Mission types
    is_plot_mission = models.BooleanField(
        default=False,
        help_text="Is this a storyteller-created plot mission?"
    )

    # DM Assignment
    dungeon_master = models.ForeignKey(
        ObjectDB,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dm_missions',
        help_text="Player assigned as DM for this mission"
    )

    # Rewards
    base_gold_reward = models.IntegerField(
        default=0,
        help_text="Base gold reward"
    )

    experience_reward = models.IntegerField(
        default=0,
        help_text="Experience points awarded"
    )

    # Loot generation info
    loot_tier_weights = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON dict of tier weights: {'tier_1': 50, 'tier_2': 30, 'tier_3': 15, 'tier_4': 5}"
    )

    # For plot missions: 2.5x artifact weight
    artifact_multiplier = models.FloatField(
        default=1.0,
        help_text="Multiplier for Tier IV (artifact) drops. Plot missions get 2.5x"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this mission currently active?"
    )

    is_completed = models.BooleanField(
        default=False,
        help_text="Has this mission been completed?"
    )

    # Participants
    participants = models.ManyToManyField(
        ObjectDB,
        related_name='participated_missions',
        blank=True,
        help_text="Characters participating in this mission"
    )

    created_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_date']
        verbose_name = "Mission"
        verbose_name_plural = "Missions"

    def __str__(self):
        status = "Active" if self.is_active else "Completed" if self.is_completed else "Inactive"
        return f"{self.name} ({self.get_danger_level_display()}) - {status}"

    def set_default_loot_weights(self):
        """Set default loot tier weights based on danger level."""
        weights = {
            DangerLevel.SAFE: {'tier_1': 90, 'tier_2': 10, 'tier_3': 0, 'tier_4': 0},
            DangerLevel.LOW: {'tier_1': 70, 'tier_2': 25, 'tier_3': 5, 'tier_4': 0},
            DangerLevel.MODERATE: {'tier_1': 50, 'tier_2': 35, 'tier_3': 14, 'tier_4': 1},
            DangerLevel.HIGH: {'tier_1': 30, 'tier_2': 40, 'tier_3': 27, 'tier_4': 3},
            DangerLevel.CRITICAL: {'tier_1': 10, 'tier_2': 30, 'tier_3': 50, 'tier_4': 10}
        }

        self.loot_tier_weights = weights.get(self.danger_level, weights[DangerLevel.LOW])

        # Plot missions get 2.5x artifact weight
        if self.is_plot_mission:
            self.artifact_multiplier = 2.5
        else:
            self.artifact_multiplier = 1.0

        self.save()

    def calculate_rewards(self):
        """Calculate rewards based on danger level."""
        gold_values = {
            DangerLevel.SAFE: 10,
            DangerLevel.LOW: 50,
            DangerLevel.MODERATE: 150,
            DangerLevel.HIGH: 400,
            DangerLevel.CRITICAL: 1000
        }

        xp_values = {
            DangerLevel.SAFE: 5,
            DangerLevel.LOW: 15,
            DangerLevel.MODERATE: 40,
            DangerLevel.HIGH: 100,
            DangerLevel.CRITICAL: 250
        }

        self.base_gold_reward = gold_values.get(self.danger_level, 50)
        self.experience_reward = xp_values.get(self.danger_level, 15)

        # Plot missions get bonus rewards
        if self.is_plot_mission:
            self.base_gold_reward = int(self.base_gold_reward * 1.5)
            self.experience_reward = int(self.experience_reward * 1.5)

        self.save()


class MissionLog(models.Model):
    """
    Log of mission activities and completion.
    """
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name='logs',
        help_text="Mission this log belongs to"
    )

    character = models.ForeignKey(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='mission_logs',
        help_text="Character involved in this log"
    )

    action_type = models.CharField(
        max_length=50,
        help_text="Type of action (joined, left, completed, failed, etc.)"
    )

    description = models.TextField(
        help_text="Description of what happened"
    )

    rewards_received = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON dict of rewards: {'gold': 100, 'xp': 50, 'items': [...]}"
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Mission Log"
        verbose_name_plural = "Mission Logs"

    def __str__(self):
        return f"{self.character.db_key} - {self.action_type} in {self.mission.name}"


class ExtractionResource(models.Model):
    """
    Defines what resources can be extracted from different biomes.
    """
    biome = models.CharField(
        max_length=20,
        choices=BiomeType.choices,
        help_text="Biome this resource appears in"
    )

    resource_name = models.CharField(
        max_length=100,
        help_text="Name of the resource"
    )

    item_template = models.ForeignKey(
        'ItemTemplate',
        on_delete=models.CASCADE,
        related_name='extraction_sources',
        help_text="Item template for this resource"
    )

    extraction_difficulty = models.IntegerField(
        default=10,
        help_text="CR to extract this resource"
    )

    base_quantity_min = models.IntegerField(
        default=1,
        help_text="Minimum quantity extracted on success"
    )

    base_quantity_max = models.IntegerField(
        default=5,
        help_text="Maximum quantity extracted on success"
    )

    danger_increase_per_extraction = models.IntegerField(
        default=5,
        help_text="How much the danger timer increases per extraction"
    )

    class Meta:
        ordering = ['biome', 'resource_name']
        unique_together = ['biome', 'resource_name']
        verbose_name = "Extraction Resource"
        verbose_name_plural = "Extraction Resources"

    def __str__(self):
        return f"{self.resource_name} from {self.get_biome_display()}"


class BiomeMobTemplate(models.Model):
    """
    Templates for mobs/enemies that spawn in different biomes.
    """
    biome = models.CharField(
        max_length=20,
        choices=BiomeType.choices,
        help_text="Biome this mob spawns in"
    )

    name = models.CharField(
        max_length=100,
        help_text="Name of the mob type"
    )

    description = models.TextField(
        help_text="Description of the mob"
    )

    # Combat stats
    base_hp = models.IntegerField(
        default=50,
        help_text="Base HP for this mob type"
    )

    stats = models.JSONField(
        default=dict,
        help_text="JSON dict of stats: {'strength': 5, 'agility': 4, ...}"
    )

    skills = models.JSONField(
        default=dict,
        help_text="JSON dict of skills: {'blades': 3, 'athletics': 2, ...}"
    )

    # Loot
    gold_drop_min = models.IntegerField(default=0)
    gold_drop_max = models.IntegerField(default=10)

    loot_table = models.JSONField(
        default=list,
        blank=True,
        help_text="JSON list of possible loot drops"
    )

    spawn_weight = models.IntegerField(
        default=10,
        help_text="Weight for random spawning (higher = more common)"
    )

    class Meta:
        ordering = ['biome', 'name']
        verbose_name = "Biome Mob Template"
        verbose_name_plural = "Biome Mob Templates"

    def __str__(self):
        return f"{self.name} ({self.get_biome_display()})"
