"""
Witcher RPG Models
Model-driven design for character creation and management.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from evennia.objects.models import ObjectDB


class Country(models.Model):
    """
    Represents a country/nation in the Witcher universe.
    Each country provides a bonus to one non-physical stat.
    """

    COUNTRY_CHOICES = [
        ('nilfgaard', 'Nilfgaardian Empire'),
        ('temeria', 'Temeria'),
        ('redania', 'Redania'),
        ('skellige', 'Skellige'),
        ('kovir', 'Kovir and Poviss'),
        ('cintra', 'Cintra'),
        ('aedirn', 'Aedirn'),
        ('kaedwen', 'Kaedwen'),
        ('lyria', 'Lyria and Rivia'),
        ('cidaris', 'Cidaris'),
    ]

    name = models.CharField(
        max_length=50,
        choices=COUNTRY_CHOICES,
        unique=True,
        help_text="Country name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the country and its culture"
    )

    # Stat bonus (non-physical only: Mental or Social)
    bonus_stat = models.CharField(
        max_length=20,
        choices=[
            ('wit', 'Wit'),
            ('intelligence', 'Intelligence'),
            ('willpower', 'Willpower'),
            ('perception', 'Perception'),
            ('charm', 'Charm'),
            ('appearance', 'Appearance'),
            ('graces', 'Graces'),
            ('cunning', 'Cunning'),
        ],
        help_text="Non-physical stat that receives +1 bonus"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return f"{self.get_name_display()} (+1 {self.bonus_stat.title()})"


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

    # Starting skill package
    default_skills = models.JSONField(
        default=dict,
        blank=True,
        help_text="Starting skill levels for this vocation: {'blades': 3, 'athletics': 2, ...}"
    )

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

    # Support skills
    resistance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Physical resistance, damage reduction (used for soak)"
    )
    leadership = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Military leadership, commanding troops, inspiring allies"
    )
    tactics = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Tactical planning, battlefield strategy, military knowledge"
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
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='characters',
        help_text="Country of origin (provides +1 to a non-physical stat)"
    )
    background = models.TextField(
        blank=True,
        help_text="Character background and history"
    )

    # Race and combat specialization
    race = models.CharField(
        max_length=50,
        choices=[('human', 'Human'), ('elf', 'Elf'), ('dwarf', 'Dwarf')],
        default='human',
        help_text="Character's race"
    )
    witcher_style = models.CharField(
        max_length=50,
        choices=[
            ('none', 'None'),
            ('cat', 'School of the Cat'),
            ('viper', 'School of the Viper'),
            ('bear', 'School of the Bear'),
            ('eagle', 'School of the Eagle'),
            ('dragon', 'School of the Dragon'),
            ('basilisk', 'School of the Basilisk'),
        ],
        default='none',
        blank=True,
        help_text="Witcher school style (only for Witcher vocation)"
    )

    # Social rank and standing
    SOCIAL_RANK_CHOICES = [
        (1, 'Rank 1 - Outcast (+5 CR: tests harder)'),
        (2, 'Rank 2 - Commoner (+0 CR: normal)'),
        (3, 'Rank 3 - Knight/Small Gentry (-5 CR: tests easier)'),
        (4, 'Rank 4 - Landed Gentry (-10 CR: tests easier)'),
        (5, 'Rank 5 - Royalty (-20 CR: tests much easier)'),
    ]
    social_rank = models.IntegerField(
        choices=SOCIAL_RANK_CHOICES,
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Social standing (affects CR for most rolls). Witchers: 1-2, Sorcerers: 3-4, Others: 1-5"
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
        Get the effective value of a stat including vocation and country modifiers.

        Args:
            stat_name (str): Name of the stat (e.g., 'strength', 'agility')

        Returns:
            int: The effective stat value
        """
        base_value = getattr(self.stats, stat_name, 0)
        vocation_mod = getattr(self.vocation, f"{stat_name}_mod", 0)

        # Add country bonus if applicable
        country_mod = 0
        if self.country and self.country.bonus_stat == stat_name:
            country_mod = 1

        return base_value + vocation_mod + country_mod

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

    def get_race_modifiers(self):
        """
        Get racial modifiers for this character.

        Returns:
            dict: Racial modifiers
        """
        modifiers = {
            'human': {
                'magic_cr_modifier': 0,
                'damage_taken_modifier': 1.0,
                'description': 'Balanced and adaptable'
            },
            'elf': {
                'magic_cr_modifier': -5,  # Easier spell casting
                'damage_taken_modifier': 1.2,  # Takes more damage
                'description': 'Natural magical affinity but fragile'
            },
            'dwarf': {
                'magic_cr_modifier': 5,  # Harder spell casting
                'damage_taken_modifier': 0.8,  # Takes less damage
                'description': 'Sturdy and resilient but magically resistant'
            }
        }
        return modifiers.get(self.race, modifiers['human'])

    def get_witcher_style_bonuses(self):
        """
        Get bonuses from Witcher fighting style.

        Returns:
            dict: Style bonuses or None if not a Witcher or no style chosen
        """
        if self.witcher_style == 'none' or self.vocation.name != 'witcher':
            return None

        styles = {
            'cat': {
                'agility': 2,
                'reflexes': 1,
                'description': 'Fast and agile, focused on speed and precision',
                'special': 'Extra dodge chance in light armor'
            },
            'viper': {
                'cunning': 2,
                'agility': 1,
                'description': 'Deceptive and tactical, uses poisons and traps',
                'special': 'Bonus to alchemy when crafting poisons'
            },
            'bear': {
                'strength': 2,
                'endurance': 2,
                'agility': -1,
                'description': 'Powerful and heavily armored, trades speed for durability',
                'special': 'Can wear heavy armor without penalty'
            },
            'eagle': {
                'perception': 2,
                'wit': 1,
                'description': 'Tactical and observant, excels at reading opponents',
                'special': 'Bonus to initiative rolls'
            },
            'dragon': {
                'intelligence': 1,
                'willpower': 1,
                'perception': 1,
                'description': 'Balanced and disciplined, masters of sign magic',
                'special': 'Enhanced sign intensity'
            },
            'basilisk': {
                'reflexes': 1,
                'endurance': 1,
                'wit': 1,
                'description': 'Adaptable and versatile, quick to adjust tactics',
                'special': 'Can change stance as a free action once per round'
            }
        }
        return styles.get(self.witcher_style)

    def get_total_effective_stat(self, stat_name):
        """
        Get the total effective stat including vocation AND witcher style bonuses.

        Args:
            stat_name (str): Name of the stat

        Returns:
            int: Total effective stat
        """
        base = self.get_effective_stat(stat_name)  # Includes vocation mods

        # Add Witcher style bonuses if applicable
        if self.witcher_style != 'none' and self.vocation.name == 'witcher':
            style_bonuses = self.get_witcher_style_bonuses()
            if style_bonuses and stat_name in style_bonuses:
                base += style_bonuses[stat_name]

        return base

    def get_appearance_modifier(self, context='general', target_gender=None):
        """
        Get appearance modifier with special handling for Witchers.

        Witchers have no general appearance penalty, but gain +3 to Appearance
        for seduction rolls against females (lore-accurate to The Witcher series).

        Args:
            context (str): 'general', 'seduction', 'intimidation', etc.
            target_gender (str): 'male', 'female', None

        Returns:
            int: Appearance modifier
        """
        # Base vocation modifier
        base_mod = self.vocation.appearance_mod

        # Special Witcher mechanic
        if self.vocation.name == 'witcher':
            if context == 'seduction' and target_gender == 'female':
                return 3  # Lore-accurate: Witchers are attractive to women despite mutations
            # No penalty for general appearance (mutations visible but not necessarily ugly)
            return 0

        return base_mod

    def apply_skill_package(self):
        """
        Apply the vocation's default skill package to this character's skills.
        Should be called during character creation.

        Returns:
            dict: Skills that were applied
        """
        if not self.vocation.default_skills:
            return {}

        applied_skills = {}

        for skill_name, skill_level in self.vocation.default_skills.items():
            # Set the skill level
            if hasattr(self.skills, skill_name):
                setattr(self.skills, skill_name, skill_level)
                applied_skills[skill_name] = skill_level
            else:
                print(f"Warning: Skill '{skill_name}' not found on CharacterSkills")

        # Save the skills
        self.skills.save()

        return applied_skills

    # Character Creation Constants
    STAT_POINTS = 24  # Points to distribute beyond base 1 in each stat
    SKILL_POINTS = 25  # Points for skills

    @staticmethod
    def calculate_skill_cost(skill_level):
        """
        Calculate the cost for a given skill level.
        Skills 0-4 cost 1 point per level.
        Skills 5+ cost 2 points per level above 4.

        Args:
            skill_level (int): Desired skill level

        Returns:
            int: Total cost in points
        """
        if skill_level <= 4:
            return skill_level
        else:
            # 4 points to get to 4, then 2 points per level above 4
            return 4 + ((skill_level - 4) * 2)

    @staticmethod
    def validate_skill_allocation(skills_dict):
        """
        Validate skill point allocation.

        Args:
            skills_dict (dict): Dictionary of skill_name: skill_level

        Returns:
            tuple: (is_valid, error_message)
        """
        total_cost = 0
        skills_at_five_or_above = 0

        for skill_name, skill_level in skills_dict.items():
            if skill_level < 0:
                return (False, f"Skill '{skill_name}' cannot be negative.")

            if skill_level > 10:
                return (False, f"Skill '{skill_name}' cannot exceed 10.")

            # Count skills at 5 or above
            if skill_level >= 5:
                skills_at_five_or_above += 1

            # Calculate cost
            total_cost += WitcherCharacter.calculate_skill_cost(skill_level)

        # Check restrictions
        if skills_at_five_or_above > 1:
            return (False, "You can only have ONE skill starting at 5 or higher.")

        if total_cost > WitcherCharacter.SKILL_POINTS:
            return (False, f"Total skill cost ({total_cost}) exceeds available points ({WitcherCharacter.SKILL_POINTS}).")

        return (True, "")

    @staticmethod
    def validate_stat_allocation(stats_dict):
        """
        Validate stat point allocation.
        Each stat starts at 1, player gets STAT_POINTS to distribute.

        Args:
            stats_dict (dict): Dictionary of stat_name: stat_value (includes the base 1)

        Returns:
            tuple: (is_valid, error_message, points_spent)
        """
        total_points_spent = 0

        for stat_name, stat_value in stats_dict.items():
            if stat_value < 1:
                return (False, f"Stat '{stat_name}' cannot be below 1.", 0)

            if stat_value > 10:
                return (False, f"Stat '{stat_name}' cannot exceed 10.", 0)

            # Points spent = value - 1 (since base is 1)
            total_points_spent += (stat_value - 1)

        if total_points_spent > WitcherCharacter.STAT_POINTS:
            return (False, f"Total stat points ({total_points_spent}) exceeds available points ({WitcherCharacter.STAT_POINTS}).", total_points_spent)

        return (True, "", total_points_spent)

    def get_social_rank_cr_modifier(self):
        """
        Get CR modifier based on social rank.
        Lower rank = increase CR (outcasts face more challenges)
        Higher rank = reduce CR (privilege makes life easier)

        Returns:
            int: CR modifier applied to difficulty (positive = harder, negative = easier)
        """
        rank_modifiers = {
            1: 5,   # Outcast: +5 CR (tests are harder - discrimination, prejudice)
            2: 0,   # Commoner: No modifier
            3: -5,  # Knight/Small Gentry: -5 CR (tests are easier)
            4: -10, # Landed Gentry: -10 CR (tests are easier)
            5: -20, # Royalty: -20 CR (tests are much easier - privilege)
        }
        return rank_modifiers.get(self.social_rank, 0)

    def get_social_rank_display_full(self):
        """Get full display of social rank with CR modifier."""
        rank_names = {
            1: 'Outcast',
            2: 'Commoner',
            3: 'Knight/Small Gentry',
            4: 'Landed Gentry',
            5: 'Royalty',
        }
        modifier = self.get_social_rank_cr_modifier()
        modifier_str = f"{modifier:+d}" if modifier != 0 else "+0"
        return f"Rank {self.social_rank} - {rank_names.get(self.social_rank, 'Unknown')} ({modifier_str} CR)"

    @staticmethod
    def get_max_rank_for_vocation(vocation_name):
        """
        Get maximum allowed social rank for a vocation.

        Args:
            vocation_name (str): Name of the vocation

        Returns:
            int: Maximum allowed rank (1-5)
        """
        rank_limits = {
            'witcher': 2,      # Witchers: outcasts, max rank 2 (commoner)
            'sorcerer': 4,     # Sorcerers: max rank 4 (landed gentry)
            # All others can go to rank 5
        }
        return rank_limits.get(vocation_name, 5)

    def validate_social_rank(self):
        """
        Validate that social rank is within vocation limits.

        Returns:
            tuple: (is_valid, error_message)
        """
        max_rank = WitcherCharacter.get_max_rank_for_vocation(self.vocation.name)

        if self.social_rank > max_rank:
            return (False, f"{self.vocation.get_name_display()} can only have rank {max_rank} or lower.")

        # Witchers should really be rank 1 unless they're leaders
        if self.vocation.name == 'witcher' and self.social_rank > 1:
            return (True, f"Warning: Most Witchers are Rank 1 (Outcast). Rank 2 is for leaders like Vesemir.")

        return (True, "")
