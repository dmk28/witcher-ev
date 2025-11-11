"""
Django Admin configuration for Witcher RPG models.
Provides intuitive interfaces for managing vocations, characters, stats, and skills.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Vocation,
    VocationFeat,
    CharacterStats,
    CharacterSkills,
    WitcherCharacter
)
from .combat_models import (
    Race,
    WitcherStyle,
    MagicElement,
    CombatEncounter,
    CombatParticipant
)
from .item_models import (
    ItemTemplate,
    InventoryItem,
    BankStorage,
    Currency
)
from .room_models import (
    WitcherRoom,
    Mission,
    MissionLog,
    ExtractionResource,
    BiomeMobTemplate
)


class VocationFeatInline(admin.TabularInline):
    """Inline admin for managing feats within vocation admin."""
    model = VocationFeat
    extra = 1
    fields = ['name', 'description', 'bonus_stat', 'bonus_dice', 'trigger_condition']


@admin.register(Vocation)
class VocationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing vocations.
    Includes inline editing of feats and organized fieldsets.
    """
    list_display = [
        'name',
        'stat_modifiers_summary',
        'skill_access_summary',
        'feat_count'
    ]
    list_filter = ['has_alchemy', 'has_magery', 'has_sign_sorcery', 'has_crafting']
    search_fields = ['name', 'description']
    inlines = [VocationFeatInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Physical Stat Modifiers', {
            'fields': (
                ('strength_mod', 'agility_mod'),
                ('endurance_mod', 'reflexes_mod')
            ),
            'classes': ['collapse']
        }),
        ('Mental Stat Modifiers', {
            'fields': (
                ('wit_mod', 'intelligence_mod'),
                ('willpower_mod', 'perception_mod')
            ),
            'classes': ['collapse']
        }),
        ('Social Stat Modifiers', {
            'fields': (
                ('charm_mod', 'appearance_mod'),
                ('graces_mod', 'cunning_mod')
            ),
            'classes': ['collapse']
        }),
        ('Skill Access', {
            'fields': (
                'has_alchemy',
                'has_magery',
                'has_sign_sorcery',
                'has_crafting'
            )
        }),
    )

    def stat_modifiers_summary(self, obj):
        """Display a summary of non-zero stat modifiers."""
        mods = []
        stat_names = [
            'strength', 'agility', 'endurance', 'reflexes',
            'wit', 'intelligence', 'willpower', 'perception',
            'charm', 'appearance', 'graces', 'cunning'
        ]
        for stat in stat_names:
            mod = getattr(obj, f'{stat}_mod', 0)
            if mod != 0:
                mods.append(f"{stat.upper()[:3]}{mod:+d}")
        return ', '.join(mods) if mods else 'None'
    stat_modifiers_summary.short_description = 'Stat Modifiers'

    def skill_access_summary(self, obj):
        """Display which special skills are available."""
        access = []
        if obj.has_alchemy:
            access.append('Alchemy')
        if obj.has_magery:
            access.append('Magery')
        if obj.has_sign_sorcery:
            access.append('Signs')
        if obj.has_crafting:
            access.append('Crafting')
        return ', '.join(access) if access else 'Standard'
    skill_access_summary.short_description = 'Skill Access'

    def feat_count(self, obj):
        """Display the number of feats for this vocation."""
        count = obj.feats.count()
        return f"{count} feat{'s' if count != 1 else ''}"
    feat_count.short_description = 'Feats'


@admin.register(VocationFeat)
class VocationFeatAdmin(admin.ModelAdmin):
    """Admin interface for managing individual feats."""
    list_display = ['name', 'vocation', 'bonus_display', 'trigger_condition']
    list_filter = ['vocation', 'bonus_stat']
    search_fields = ['name', 'description', 'vocation__name']
    list_select_related = ['vocation']

    fieldsets = (
        ('Basic Information', {
            'fields': ('vocation', 'name', 'description')
        }),
        ('Mechanical Effects', {
            'fields': (
                'bonus_stat',
                'bonus_dice',
                'trigger_condition'
            )
        }),
    )

    def bonus_display(self, obj):
        """Display the bonus in a readable format."""
        if obj.bonus_dice and obj.bonus_stat:
            return f"+{obj.bonus_dice}d to {obj.bonus_stat}"
        elif obj.bonus_dice:
            return f"+{obj.bonus_dice}d"
        return "No dice bonus"
    bonus_display.short_description = 'Bonus'


@admin.register(CharacterStats)
class CharacterStatsAdmin(admin.ModelAdmin):
    """Admin interface for managing character stats."""
    list_display = [
        'id',
        'physical_stats',
        'mental_stats',
        'social_stats'
    ]

    fieldsets = (
        ('Physical Stats', {
            'fields': (
                ('strength', 'agility'),
                ('endurance', 'reflexes')
            )
        }),
        ('Mental Stats', {
            'fields': (
                ('wit', 'intelligence'),
                ('willpower', 'perception')
            )
        }),
        ('Social Stats', {
            'fields': (
                ('charm', 'appearance'),
                ('graces', 'cunning')
            )
        }),
    )

    def physical_stats(self, obj):
        return f"STR:{obj.strength} AGI:{obj.agility} END:{obj.endurance} REF:{obj.reflexes}"
    physical_stats.short_description = 'Physical'

    def mental_stats(self, obj):
        return f"WIT:{obj.wit} INT:{obj.intelligence} WIL:{obj.willpower} PER:{obj.perception}"
    mental_stats.short_description = 'Mental'

    def social_stats(self, obj):
        return f"CHA:{obj.charm} APP:{obj.appearance} GRA:{obj.graces} CUN:{obj.cunning}"
    social_stats.short_description = 'Social'


@admin.register(CharacterSkills)
class CharacterSkillsAdmin(admin.ModelAdmin):
    """Admin interface for managing character skills."""
    list_display = [
        'id',
        'combat_skills',
        'special_skills',
        'crafting_display'
    ]

    fieldsets = (
        ('Weapon Skills', {
            'fields': (
                ('blades', 'axes', 'maces'),
                ('spears', 'crossbows', 'brawling')
            )
        }),
        ('Special Skills', {
            'fields': (
                'alchemy',
                'magery',
                'sign_sorcery'
            )
        }),
        ('Crafting', {
            'fields': (
                'crafting_type',
                'crafting_skill'
            )
        }),
        ('General Skills', {
            'fields': ('athletics',)
        }),
    )

    def combat_skills(self, obj):
        skills = [
            f"Blades:{obj.blades}",
            f"Axes:{obj.axes}",
            f"Maces:{obj.maces}",
            f"Spears:{obj.spears}",
            f"Xbows:{obj.crossbows}",
            f"Brawl:{obj.brawling}"
        ]
        return ', '.join(skills)
    combat_skills.short_description = 'Combat'

    def special_skills(self, obj):
        return f"Alch:{obj.alchemy} Mag:{obj.magery} Signs:{obj.sign_sorcery}"
    special_skills.short_description = 'Special'

    def crafting_display(self, obj):
        if obj.crafting_type != 'none':
            return f"{obj.get_crafting_type_display()}:{obj.crafting_skill}"
        return "None"
    crafting_display.short_description = 'Crafting'


class CharacterStatsInline(admin.StackedInline):
    """Inline for editing stats within character admin."""
    model = CharacterStats
    can_delete = False
    fields = (
        ('strength', 'agility', 'endurance', 'reflexes'),
        ('wit', 'intelligence', 'willpower', 'perception'),
        ('charm', 'appearance', 'graces', 'cunning')
    )


class CharacterSkillsInline(admin.StackedInline):
    """Inline for editing skills within character admin."""
    model = CharacterSkills
    can_delete = False
    fields = (
        ('blades', 'axes', 'maces', 'spears', 'crossbows', 'brawling'),
        ('alchemy', 'magery', 'sign_sorcery'),
        ('crafting_type', 'crafting_skill'),
        'athletics'
    )


@admin.register(WitcherCharacter)
class WitcherCharacterAdmin(admin.ModelAdmin):
    """
    Main admin interface for managing characters.
    Includes inline editing of stats and skills.
    """
    list_display = [
        'character_name',
        'vocation',
        'nation',
        'experience_points',
        'created_date'
    ]
    list_filter = ['vocation', 'nation', 'created_date']
    search_fields = ['character_name', 'background', 'nation']
    readonly_fields = ['created_date', 'modified_date', 'effective_stats_display']
    list_select_related = ['vocation', 'stats', 'skills']

    fieldsets = (
        ('Character Identity', {
            'fields': ('db_object', 'character_name', 'vocation')
        }),
        ('Background', {
            'fields': ('nation', 'background')
        }),
        ('Progression', {
            'fields': ('experience_points',)
        }),
        ('Effective Stats (with Vocation Bonuses)', {
            'fields': ('effective_stats_display',),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('created_date', 'modified_date'),
            'classes': ['collapse']
        }),
    )

    # Note: Inlines would go here if stats/skills didn't have their own admin
    # For now, they're managed separately for more flexibility

    def effective_stats_display(self, obj):
        """Display all effective stats including vocation modifiers."""
        stats = obj.get_all_effective_stats()

        html = "<div style='font-family: monospace;'>"
        html += "<strong>Physical:</strong> "
        html += f"STR: {stats['strength']} | "
        html += f"AGI: {stats['agility']} | "
        html += f"END: {stats['endurance']} | "
        html += f"REF: {stats['reflexes']}<br>"

        html += "<strong>Mental:</strong> "
        html += f"WIT: {stats['wit']} | "
        html += f"INT: {stats['intelligence']} | "
        html += f"WIL: {stats['willpower']} | "
        html += f"PER: {stats['perception']}<br>"

        html += "<strong>Social:</strong> "
        html += f"CHA: {stats['charm']} | "
        html += f"APP: {stats['appearance']} | "
        html += f"GRA: {stats['graces']} | "
        html += f"CUN: {stats['cunning']}"
        html += "</div>"

        return format_html(html)
    effective_stats_display.short_description = 'Effective Stats'

    def save_model(self, request, obj, form, change):
        """Ensure stats and skills are created if they don't exist."""
        # Create stats if needed
        if not hasattr(obj, 'stats') or obj.stats is None:
            stats = CharacterStats.objects.create()
            obj.stats = stats

        # Create skills if needed
        if not hasattr(obj, 'skills') or obj.skills is None:
            skills = CharacterSkills.objects.create()
            obj.skills = skills

        super().save_model(request, obj, form, change)


# Combat System Admin

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    """Admin for race management."""
    list_display = ['name', 'magic_cr_modifier', 'damage_taken_modifier']
    fields = ['name', 'description', 'magic_cr_modifier', 'damage_taken_modifier']


@admin.register(WitcherStyle)
class WitcherStyleAdmin(admin.ModelAdmin):
    """Admin for Witcher fighting styles."""
    list_display = ['name', 'stat_bonuses_display']
    fields = [
        'name', 'description',
        ('agility_bonus', 'reflexes_bonus'),
        ('strength_bonus', 'endurance_bonus', 'perception_bonus'),
        'special_ability'
    ]

    def stat_bonuses_display(self, obj):
        bonuses = []
        if obj.agility_bonus: bonuses.append(f"AGI+{obj.agility_bonus}")
        if obj.reflexes_bonus: bonuses.append(f"REF+{obj.reflexes_bonus}")
        if obj.strength_bonus: bonuses.append(f"STR+{obj.strength_bonus}")
        if obj.endurance_bonus: bonuses.append(f"END+{obj.endurance_bonus}")
        if obj.perception_bonus: bonuses.append(f"PER+{obj.perception_bonus}")
        return ', '.join(bonuses) if bonuses else 'None'
    stat_bonuses_display.short_description = 'Stat Bonuses'


@admin.register(MagicElement)
class MagicElementAdmin(admin.ModelAdmin):
    """Admin for magic elements."""
    list_display = ['name', 'description']
    fields = ['name', 'description']


class CombatParticipantInline(admin.TabularInline):
    """Inline for combat participants."""
    model = CombatParticipant
    extra = 0
    fields = [
        'character', 'initiative_order', 'current_hp', 'max_hp',
        'stance', 'is_active'
    ]
    readonly_fields = ['initiative_order']


@admin.register(CombatEncounter)
class CombatEncounterAdmin(admin.ModelAdmin):
    """Admin for managing combat encounters."""
    list_display = ['name', 'location', 'current_round', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CombatParticipantInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'is_active')
        }),
        ('Combat State', {
            'fields': ('current_round', 'current_turn_index')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(CombatParticipant)
class CombatParticipantAdmin(admin.ModelAdmin):
    """Admin for individual combat participants."""
    list_display = [
        'character', 'encounter', 'initiative_order',
        'hp_display', 'stance', 'is_active'
    ]
    list_filter = ['stance', 'is_active', 'encounter']
    search_fields = ['character__db_key']

    fieldsets = (
        ('Basic Info', {
            'fields': ('encounter', 'character', 'is_active')
        }),
        ('Initiative', {
            'fields': ('initiative_roll', 'initiative_order')
        }),
        ('Health', {
            'fields': ('current_hp', 'max_hp', 'armor_value')
        }),
        ('Combat State', {
            'fields': (
                'stance',
                'last_attack_type',
                'recovery_penalty'
            )
        }),
        ('Spell Casting', {
            'fields': (
                'is_casting',
                'spell_turns_remaining',
                'spell_name',
                'spell_difficulty',
                'spell_element'
            ),
            'classes': ['collapse']
        }),
    )

    def hp_display(self, obj):
        percent = (obj.current_hp / obj.max_hp * 100) if obj.max_hp > 0 else 0
        color = 'green' if percent > 60 else 'orange' if percent > 30 else 'red'
        return format_html(
            '<span style="color: {};">{}/{}</span>',
            color,
            obj.current_hp,
            obj.max_hp
        )
    hp_display.short_description = 'HP'

# Import additional admin classes
from .admin_items_rooms import *

