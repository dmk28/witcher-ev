"""
Additional admin classes for Items and Rooms.
This is temporarily separate to avoid file conflicts.
"""
from django.contrib import admin
from django.utils.html import format_html
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


# ===== ITEM/INVENTORY ADMIN =====

@admin.register(ItemTemplate)
class ItemTemplateAdmin(admin.ModelAdmin):
    """Admin for item templates."""
    list_display = [
        'name',
        'tier',
        'category',
        'gold_value',
        'weight',
        'is_stackable'
    ]
    list_filter = ['tier', 'category', 'is_stackable']
    search_fields = ['name', 'description']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'tier', 'category')
        }),
        ('Value & Weight', {
            'fields': (('gold_value', 'weight'), ('is_stackable', 'max_stack'))
        }),
        ('Equipment Stats', {
            'fields': ('damage_bonus', 'armor_value', 'stat_bonuses'),
            'classes': ['collapse']
        }),
        ('Special Properties', {
            'fields': ('special_ability',),
            'classes': ['collapse']
        }),
        ('Crafting', {
            'fields': (
                'required_materials',
                'crafting_skill_required',
                'crafting_difficulty'
            ),
            'classes': ['collapse']
        }),
    )


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """Admin for inventory items."""
    list_display = [
        'display_name',
        'template',
        'owner',
        'quantity',
        'is_equipped',
        'condition'
    ]
    list_filter = ['is_equipped', 'template__tier', 'template__category']
    search_fields = ['template__name', 'custom_name', 'owner__db_key']
    readonly_fields = ['acquired_date']

    fieldsets = (
        ('Basic Info', {
            'fields': ('template', 'owner', 'quantity')
        }),
        ('Customization', {
            'fields': ('custom_name', 'custom_bonuses')
        }),
        ('Status', {
            'fields': ('is_equipped', 'condition')
        }),
        ('Metadata', {
            'fields': ('acquired_date',),
            'classes': ['collapse']
        }),
    )

    def display_name(self, obj):
        if obj.custom_name:
            return format_html('<strong>{}</strong>', obj.custom_name)
        return obj.template.name
    display_name.short_description = 'Item Name'


@admin.register(BankStorage)
class BankStorageAdmin(admin.ModelAdmin):
    """Admin for bank storage."""
    list_display = ['owner', 'gold_stored', 'item_count', 'max_storage_slots', 'space_available']
    search_fields = ['owner__db_key']
    readonly_fields = ['created_date']

    fields = ['owner', 'gold_stored', 'max_storage_slots', 'created_date']

    def item_count(self, obj):
        return obj.get_item_count()
    item_count.short_description = 'Items Stored'

    def space_available(self, obj):
        used = obj.get_item_count()
        total = obj.max_storage_slots
        percent = (used / total * 100) if total > 0 else 0
        color = 'green' if percent < 70 else 'orange' if percent < 90 else 'red'
        return format_html(
            '<span style="color: {};">{}/{} ({:.0f}%)</span>',
            color, used, total, percent
        )
    space_available.short_description = 'Space'


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Admin for character currency."""
    list_display = ['character', 'gold']
    search_fields = ['character__db_key']


# ===== ROOM/MISSION ADMIN =====

@admin.register(WitcherRoom)
class WitcherRoomAdmin(admin.ModelAdmin):
    """Admin for Witcher rooms."""
    list_display = [
        'room_object',
        'room_type',
        'biome',
        'danger_level',
        'extraction_status',
        'is_mission_active'
    ]
    list_filter = ['room_type', 'biome', 'danger_level', 'is_mission_active']
    search_fields = ['room_object__db_key', 'organization']
    readonly_fields = ['created_date', 'modified_date']

    fieldsets = (
        ('Basic Information', {
            'fields': ('room_object', 'room_type', 'biome', 'danger_level')
        }),
        ('Extraction Room Data', {
            'fields': ('extraction_timer', 'available_resources'),
            'classes': ['collapse']
        }),
        ('Mission/Plot Data', {
            'fields': ('is_mission_active',)
        }),
        ('Organization', {
            'fields': ('organization',),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_date', 'modified_date'),
            'classes': ['collapse']
        }),
    )

    def extraction_status(self, obj):
        if obj.room_type != 'extraction':
            return 'N/A'

        timer = obj.extraction_timer
        color = 'green' if timer < 50 else 'orange' if timer < 80 else 'red'
        return format_html(
            '<span style="color: {};">{}/100</span>',
            color, timer
        )
    extraction_status.short_description = 'Extraction Timer'


class MissionLogInline(admin.TabularInline):
    """Inline for mission logs."""
    model = MissionLog
    extra = 0
    readonly_fields = ['timestamp']
    fields = ['character', 'action_type', 'description', 'timestamp']
    can_delete = False


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    """Admin for missions."""
    list_display = [
        'name',
        'room',
        'danger_level',
        'is_plot_mission',
        'dungeon_master',
        'status',
        'participant_count'
    ]
    list_filter = ['danger_level', 'is_plot_mission', 'is_active', 'is_completed']
    search_fields = ['name', 'description', 'room__room_object__db_key']
    filter_horizontal = ['participants']
    readonly_fields = ['created_date', 'completed_date']
    inlines = [MissionLogInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('room', 'name', 'description', 'danger_level')
        }),
        ('Mission Type', {
            'fields': ('is_plot_mission', 'artifact_multiplier')
        }),
        ('DM Assignment', {
            'fields': ('dungeon_master',)
        }),
        ('Rewards', {
            'fields': ('base_gold_reward', 'experience_reward', 'loot_tier_weights')
        }),
        ('Status', {
            'fields': ('is_active', 'is_completed', 'participants')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'completed_date'),
            'classes': ['collapse']
        }),
    )

    def status(self, obj):
        if obj.is_completed:
            return format_html('<span style="color: green;">Completed</span>')
        elif obj.is_active:
            return format_html('<span style="color: blue;">Active</span>')
        else:
            return format_html('<span style="color: gray;">Inactive</span>')
    status.short_description = 'Status'

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = '# Participants'

    def save_model(self, request, obj, form, change):
        """Auto-calculate rewards and loot weights if not set."""
        if not change or not obj.loot_tier_weights:
            obj.set_default_loot_weights()
            obj.calculate_rewards()
        super().save_model(request, obj, form, change)


@admin.register(MissionLog)
class MissionLogAdmin(admin.ModelAdmin):
    """Admin for mission logs."""
    list_display = ['mission', 'character', 'action_type', 'timestamp']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['mission__name', 'character__db_key', 'description']
    readonly_fields = ['timestamp']

    fields = ['mission', 'character', 'action_type', 'description', 'rewards_received', 'timestamp']


@admin.register(ExtractionResource)
class ExtractionResourceAdmin(admin.ModelAdmin):
    """Admin for extraction resources."""
    list_display = [
        'resource_name',
        'biome',
        'item_template',
        'extraction_difficulty',
        'quantity_range',
        'danger_increase_per_extraction'
    ]
    list_filter = ['biome']
    search_fields = ['resource_name', 'biome']

    fields = [
        ('biome', 'resource_name'),
        'item_template',
        'extraction_difficulty',
        ('base_quantity_min', 'base_quantity_max'),
        'danger_increase_per_extraction'
    ]

    def quantity_range(self, obj):
        return f"{obj.base_quantity_min}-{obj.base_quantity_max}"
    quantity_range.short_description = 'Quantity Range'


@admin.register(BiomeMobTemplate)
class BiomeMobTemplateAdmin(admin.ModelAdmin):
    """Admin for biome mob templates."""
    list_display = [
        'name',
        'biome',
        'base_hp',
        'gold_range',
        'spawn_weight'
    ]
    list_filter = ['biome']
    search_fields = ['name', 'description']

    fieldsets = (
        ('Basic Information', {
            'fields': ('biome', 'name', 'description')
        }),
        ('Combat Stats', {
            'fields': ('base_hp', 'stats', 'skills')
        }),
        ('Loot', {
            'fields': (('gold_drop_min', 'gold_drop_max'), 'loot_table')
        }),
        ('Spawning', {
            'fields': ('spawn_weight',)
        }),
    )

    def gold_range(self, obj):
        return f"{obj.gold_drop_min}-{obj.gold_drop_max}g"
    gold_range.short_description = 'Gold Drop'
