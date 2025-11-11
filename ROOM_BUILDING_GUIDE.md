# Room Building System Guide

This document explains the GM and player room building systems for the Witcher RPG MUD.

## Table of Contents
- [GM Room Builder](#gm-room-builder)
- [Player Room Builder](#player-room-builder)
- [Room Properties](#room-properties)
- [Examples](#examples)

---

## GM Room Builder

GMs have full control over room creation, editing, linking, and deletion.

### Commands

#### Create a Room
```
+roomcreate <name>
```
Creates a new room with default properties (Adventure/Plains/Safe).

**Example:**
```
+roomcreate The Rusty Sword Tavern
+roomcreate Ancient Forest Clearing
```

#### Edit Room Properties
```
+roomedit <room>/property = <value>
```

Available properties:
- `name` - Room name
- `desc` - Room description
- `type` - Room type: `adventure`, `bank`, `extraction`
- `biome` - Biome type: `forest`, `mine`, `urban`, `plains`, `mountains`, `swamp`, `desert`, `hills`, `river`, `ocean`
- `purpose` - Room purpose: `crafting`, `storage`, `residence`, `shop`, `tavern`
- `owner` - Character who owns the room
- `organization` - Organization name
- `resources` - JSON dict of available resources
- `danger` - Danger level: `safe`, `low`, `moderate`, `high`, `critical`

**Examples:**
```
+roomedit here/name = The Prancing Pony Inn
+roomedit here/desc = A cozy tavern with a roaring fireplace and the smell of fresh bread.
+roomedit here/type = bank
+roomedit here/biome = urban
+roomedit here/purpose = crafting
+roomedit here/owner = Geralt
+roomedit here/organization = Merchants Guild
+roomedit here/resources = {"iron_ore": 50, "wood": 100}
+roomedit here/danger = moderate
```

#### Link Rooms
```
+roomlink <direction> = <target room>
+roomlink/twoway <direction> = <target room>
```

Creates an exit in the specified direction. Use `/twoway` to automatically create a return exit.

**Examples:**
```
+roomlink north = Town Square
+roomlink/twoway east = Ancient Forest
+roomlink up = Tower Top
```

Valid directions:
- Cardinal: `north`, `south`, `east`, `west`
- Diagonal: `northeast`, `southeast`, `southwest`, `northwest`
- Vertical: `up`, `down`
- In/Out: `in`, `out`

#### Delete a Room
```
+roomdelete <room name>
+roomdelete here
```

Permanently deletes a room and all its WitcherRoom data.

**WARNING:** This cannot be undone!

---

## Player Room Builder

Players can purchase rooms for their characters to use as workshops, storage, or residences.

### Commands

#### Purchase a Room
```
+buyroom <name>
```

**Cost:** 50,000 gold crowns

Creates a new room owned by you in an urban area. Default purpose is "residence."

**Example:**
```
+buyroom Geralt's Workshop
+buyroom My Cozy Apartment
```

#### View Owned Rooms
```
+myrooms
```

Lists all rooms you own with their purposes and IDs.

#### Set Room Purpose
```
+roompurpose <room name> = <purpose>
```

Valid purposes:
- `crafting` - Acts as a workshop (enables crafting)
- `storage` - Provides bank storage access
- `residence` - For roleplay and decoration

**Examples:**
```
+roompurpose My Workshop = crafting
+roompurpose Storage Vault = storage
+roompurpose Cozy Home = residence
```

#### Sell a Room
```
+sellroom <room name>
```

**Refund:** 25,000 gold (50% of purchase price)

Permanently deletes the room and refunds half the purchase price.

**WARNING:** This cannot be undone!

---

## Room Properties

### Room Types

1. **Adventure** - Standard outdoor/exploration rooms
2. **Bank** - Bank and storage facilities
3. **Extraction** - Resource gathering locations with danger timers

### Biomes

- `forest` - Dense woods
- `mine` - Underground mining areas
- `hills` - Rolling hills
- `river` - River locations
- `ocean` - Coastal/sea areas
- `plains` - Open grasslands
- `mountains` - Mountain regions
- `swamp` - Wetlands
- `desert` - Arid regions
- `urban` - Cities and towns

### Room Purposes (Urban Only)

- `crafting` - **Workshop** - Enables crafting (must be owned by character)
- `storage` - **Warehouse** - Bank storage access
- `residence` - **Home** - Roleplay and decoration
- `shop` - **Merchant** - Player shop (future feature)
- `tavern` - **Inn** - Social gathering place

### Danger Levels

- `safe` - No danger
- `low` - Minor threats
- `moderate` - Moderate threats
- `high` - Serious danger
- `critical` - Extreme danger

---

## Examples

### Example 1: GM Creates a Crafting Workshop

```
+roomcreate Blacksmith's Forge
+roomedit here/desc = A hot, smoky forge with anvils, hammers, and glowing coals.
+roomedit here/biome = urban
+roomedit here/purpose = crafting
+roomedit here/owner = Geralt
+roomlink/twoway south = Town Square
```

### Example 2: Player Purchases Workshop

```
+buyroom Geralt's Private Workshop
+roompurpose Geralt's Private Workshop = crafting
```

Now the player can craft in their own workshop!

### Example 3: GM Creates Extraction Area

```
+roomcreate Iron Mine Entrance
+roomedit here/desc = A dark mine shaft descends into the earth, rich with ore.
+roomedit here/type = extraction
+roomedit here/biome = mine
+roomedit here/resources = {"iron_ore": 100, "coal": 50}
+roomedit here/danger = moderate
+roomlink/twoway down = Deep Mine Shaft
```

### Example 4: GM Creates Quest Location

```
+roomcreate Haunted Castle Courtyard
+roomedit here/desc = Overgrown courtyard with crumbling statues and an ominous atmosphere.
+roomedit here/biome = plains
+roomedit here/danger = high
+roomlink north = Castle Gates
```

---

## Integration with Other Systems

### Crafting System
- Rooms with `purpose = crafting` in `biome = urban` owned by the character enable crafting
- See `is_valid_workshop()` in `world/witcher_rpg/room_models.py:154`

### Extraction System
- Rooms with `type = extraction` allow resource gathering
- Timer increments per extraction, spawns missions at 100
- See `increment_extraction_timer()` in `world/witcher_rpg/room_models.py:135`

### Bank System
- Rooms with `purpose = storage` can provide bank access (future feature)

### Mission System
- Rooms can host missions with rewards and loot
- Danger level affects loot tier distribution
- See `Mission` model in `world/witcher_rpg/room_models.py:182`

---

## Economic Impact

### Player Investment
- **Room Purchase:** 50,000 gold
- **Room Sale:** 25,000 gold refund (50%)
- **Net Loss per Room Sold:** 25,000 gold

### Benefits
- **Crafting Workshop:** Enables crafting without renting/borrowing
- **Storage:** Personal bank access (future)
- **Residence:** RP space, potential passive income (future)

### Example Investment
A player purchasing a crafting workshop:
1. Saves on workshop rental fees (future feature)
2. Can craft anytime without GM permission
3. Can sell workshop back for 25k if needed
4. Total investment: 50k gold (half-recoverable)

---

## Future Features

### Planned Enhancements
- **Player Shops:** Sell items while offline
- **Rental System:** Rent workshops/storage to other players
- **Room Upgrades:** Purchase expansions, decorations, security
- **Passive Income:** Generate gold from shops/rentals
- **Room Capacity:** Limit on player-owned rooms per character

### Workshop Rental (Planned)
- GM-owned workshops: 100-500 gold per crafting session
- Player-owned workshops: Free for owner, rentable to others

---

## Technical Details

### Models Used
- `WitcherRoom` - Extended room data (world/witcher_rpg/room_models.py)
- `WitcherCharacter` - Character data with gold tracking
- `ObjectDB` - Evennia room object

### Files
- `commands/building_commands.py` - All room building commands
- `world/witcher_rpg/room_models.py` - Room data models
- `commands/default_cmdsets.py` - Command registration

### Permissions
- **GM Commands:** Require `perm(Builder)` permission
- **Player Commands:** Available to all characters with sufficient gold
