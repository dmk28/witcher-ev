"""
Witcher RPG Models
Model-driven design for character creation and management.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB


class Vocation(models.Model):
    """
    Represents a character vocation/class in the Witcher universe.
    Each vocation has specific stat modifiers and access to certain abilities.
    """

    VOCATION_CHOICES = [
        ('soldier', 'Soldier'),
        ('bladesman', 'Bladesman'),
        ('knight', 'Knight'),
        ('inquisitor', 'Inquisitor'),
        ('sorcerer', 'Sorcerer/ess'),
        ('witcher', 'Witcher'),
        ('courtesan', 'Courtesan'),
        ('infiltrator', 'Infiltrator'),
        ('noble', 'Noble'),
        ('alchemist', 'Alchemist'),
        ('merchant', 'Merchant'),
    ]

    name = models.CharField(
        max_length=50,
        choices=VOCATION_CHOICES,
        unique=True,
        help_text="The vocation name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the vocation"
    )

    # Stat modifiers
    strength_mod = models.IntegerField(default=0, help_text="Strength modifier")
    agility_mod = models.IntegerField(default=0, help_text="Agility modifier")
    endurance_mod = models.IntegerField(default=0, help_text="Endurance modifier")
    reflexes_mod = models.IntegerField(default=0, help_text="Reflexes modifier")
    wit_mod = models.IntegerField(default=0, help_text="Wit modifier")
    intelligence_mod = models.IntegerField(default=0, help_text="Intelligence modifier")
    willpower_mod = models.IntegerField(default=0, help_text="Willpower modifier")
    perception_mod = models.IntegerField(default=0, help_text="Perception modifier")
    charm_mod = models.IntegerField(default=0, help_text="Charm modifier")
    appearance_mod = models.IntegerField(default=0, help_text="Appearance modifier")
    graces_mod = models.IntegerField(default=0, help_text="Graces modifier")
    cunning_mod = models.IntegerField(default=0, help_text="Cunning modifier")

    # Skill access
    has_alchemy = models.BooleanField(default=False, help_text="Access to Alchemy")
    has_magery = models.BooleanField(default=False, help_text="Access to Magery")
    has_sign_sorcery = models.BooleanField(default=False, help_text="Access to Sign Sorcery")
    has_crafting = models.BooleanField(default=False, help_text="Access to Crafting skills")

    class Meta:
        ordering = ['name']
        verbose_name = "Vocation"
        verbose_name_plural = "Vocations"

    def __str__(self):
        return self.get_name_display()


class VocationFeat(models.Model):
    """
    Represents feats that are specific to vocations.
    """
    vocation = models.ForeignKey(
        Vocation,
        on_delete=models.CASCADE,
        related_name='feats',
        help_text="The vocation this feat belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the feat"
    )
    description = models.TextField(
        help_text="Description of what the feat does"
    )

    # Dice bonuses for various stats/skills
    bonus_stat = models.CharField(
        max_length=50,
        blank=True,
        help_text="Which stat this feat provides bonus dice for (e.g., 'strength', 'agility')"
    )
    bonus_dice = models.IntegerField(
        default=0,
        help_text="Number of bonus dice granted"
    )

    # For situational bonuses
    trigger_condition = models.CharField(
        max_length=200,
        blank=True,
        help_text="When this feat activates (e.g., 'defensive maneuvers', 'using swords')"
    )

    class Meta:
        ordering = ['vocation', 'name']
        verbose_name = "Vocation Feat"
        verbose_name_plural = "Vocation Feats"

    def __str__(self):
        return f"{self.vocation.name}: {self.name}"


class CharacterStats(models.Model):
    """
    The 12 core stats for a Witcher RPG character.
    Physical: Strength, Agility, Endurance, Reflexes
    Mental: Wit, Intelligence, Willpower, Perception
    Social: Charm, Appearance, Graces, Cunning
    """

    # Physical stats
    strength = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Physical power and melee damage"
    )
    agility = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Speed, reflexive dodging, and finesse"
    )
    endurance = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Stamina, health, and resistance"
    )
    reflexes = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Reaction speed and initiative"
    )

    # Mental stats
    wit = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Quick thinking and cleverness"
    )
    intelligence = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Knowledge and reasoning"
    )
    willpower = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Mental fortitude and magic power"
    )
    perception = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Awareness and noticing details"
    )

    # Social stats
    charm = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Charisma and likability"
    )
    appearance = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Physical attractiveness"
    )
    graces = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Social grace and etiquette"
    )
    cunning = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Deception and manipulation"
    )

    class Meta:
        verbose_name = "Character Stats"
        verbose_name_plural = "Character Stats"

    def __str__(self):
        return f"Stats (STR:{self.strength} AGI:{self.agility} END:{self.endurance}...)"


class CharacterSkills(models.Model):
    """
    Skills available to characters in the Witcher RPG.
    Skill levels typically range from 0 (untrained) to 10 (master).
    """

    # Weapon skills
    blades = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Proficiency with swords and bladed weapons"
    )
    axes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Proficiency with axes and chopping weapons"
    )
    maces = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Proficiency with maces and blunt weapons"
    )
    spears = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Proficiency with spears and polearms"
    )
    crossbows = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Proficiency with crossbows and ranged weapons"
    )
    brawling = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Unarmed combat proficiency"
    )

    # Special skills
    alchemy = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Potion-making and alchemical knowledge (requires access)"
    )
    magery = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Spell-casting ability (requires access)"
    )
    sign_sorcery = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Witcher sign magic (requires access)"
    )

    # Crafting skills (choose one specialization)
    CRAFTING_CHOICES = [
        ('none', 'None'),
        ('smithing', 'Smithing'),
        ('carpentry', 'Carpentry'),
        ('herbalism', 'Herbalism'),
    ]
    crafting_type = models.CharField(
        max_length=20,
        choices=CRAFTING_CHOICES,
        default='none',
        help_text="Crafting specialization"
    )
    crafting_skill = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Crafting skill level"
    )

    # General skills
    athletics = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Physical fitness, running, jumping, climbing"
    )

    class Meta:
        verbose_name = "Character Skills"
        verbose_name_plural = "Character Skills"

    def __str__(self):
        return f"Skills (Blades:{self.blades} Athletics:{self.athletics}...)"


class WitcherCharacter(models.Model):
    """
    Main character model for the Witcher RPG.
    This follows the model -> typeclass pattern where the model stores data
    and the typeclass (in typeclasses/characters.py) handles behavior.
    """

    # Link to the Evennia ObjectDB (the actual character object)
    db_object = models.OneToOneField(
        ObjectDB,
        on_delete=models.CASCADE,
        related_name='witcher_character',
        help_text="The Evennia object this character data belongs to"
    )

    # Character identity
    character_name = models.CharField(
        max_length=100,
        help_text="Character's IC name"
    )
    vocation = models.ForeignKey(
        Vocation,
        on_delete=models.PROTECT,
        related_name='characters',
        help_text="Character's vocation/class"
    )

    # Link to stats and skills
    stats = models.OneToOneField(
        CharacterStats,
        on_delete=models.CASCADE,
        related_name='character',
        help_text="Character's stat block"
    )
    skills = models.OneToOneField(
        CharacterSkills,
        on_delete=models.CASCADE,
        related_name='character',
        help_text="Character's skill set"
    )

    # Additional character info
    nation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nation or origin"
    )
    background = models.TextField(
        blank=True,
        help_text="Character background and history"
    )

    # Experience and progression
    experience_points = models.IntegerField(
        default=0,
        help_text="Total experience points earned"
    )

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']
        verbose_name = "Witcher Character"
        verbose_name_plural = "Witcher Characters"

    def __str__(self):
        return f"{self.character_name} ({self.vocation})"

    def get_effective_stat(self, stat_name):
        """
        Get the effective value of a stat including vocation modifiers.

        Args:
            stat_name (str): Name of the stat (e.g., 'strength', 'agility')

        Returns:
            int: The effective stat value
        """
        base_value = getattr(self.stats, stat_name, 0)
        vocation_mod = getattr(self.vocation, f"{stat_name}_mod", 0)
        return base_value + vocation_mod

    def get_all_effective_stats(self):
        """
        Returns a dictionary of all effective stats.
        """
        stat_names = [
            'strength', 'agility', 'endurance', 'reflexes',
            'wit', 'intelligence', 'willpower', 'perception',
            'charm', 'appearance', 'graces', 'cunning'
        ]
        return {stat: self.get_effective_stat(stat) for stat in stat_names}

    def has_skill_access(self, skill_name):
        """
        Check if this character has access to a special skill based on vocation.

        Args:
            skill_name (str): Name of the skill (e.g., 'alchemy', 'magery')

        Returns:
            bool: True if character has access to this skill
        """
        access_map = {
            'alchemy': self.vocation.has_alchemy,
            'magery': self.vocation.has_magery,
            'sign_sorcery': self.vocation.has_sign_sorcery,
            'crafting': self.vocation.has_crafting,
        }
        return access_map.get(skill_name, True)  # Most skills are available to all

    def get_vocation_feats(self):
        """
        Get all feats associated with this character's vocation.
        """
        return self.vocation.feats.all()
