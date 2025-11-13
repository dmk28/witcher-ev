# Cities Quick Reference Guide
## The Northern Kingdoms - Two Major Cities

---

## Overview

The game now includes two fully realized major cities, each with distinct character and thousands of unique locations:

- **Vengerberg** (32x32 grid, 1,024 rooms) - Classic medieval city
- **Novigrad** (40x40 grid, 1,600 rooms) - Largest Free City with color-coded districts

**Total**: 2,626 rooms connected by 10,210 exits

**Travel Between Cities**: Staff-locked waystones allow instant teleportation (Builder permission required)

---

## VENGERBERG (Medium City)

**Grid**: 32x32 (1,024 rooms)
**Style**: Traditional fantasy medieval city
**Government**: Royal palace (part of larger kingdom)

### Districts

1. **Temple District** (NW City)
   - Spiritual center, Great Temple of Melitele
   - Healing services, religious guidance
   - Rows 11-16, Columns 8-15

2. **Royal Quarter** (NE City)
   - Nobility, Royal Palace, exclusive estates
   - Heavy security, restricted access
   - Rows 11-16, Columns 16-25

3. **Market Ward** (Central City) **DEFAULT HOME**
   - Central Market Square (18, 16) - starting location
   - Shops, taverns, The Prancing Pony
   - Bustling commerce and trade
   - Rows 17-20, Columns 8-25

4. **Craftsmen Quarter** (SW City)
   - The Master Forge (legendary dwarven smithy)
   - Workshops, forges, artisans
   - Rows 21-23, Columns 8-16

5. **River Ward** (SE City)
   - Docks on Pontar River
   - Harbor Master's Office, The Rusty Anchor
   - River trade and fishing
   - Rows 21-23, Columns 17-25

### Surrounding Areas

- **Northern Woods** (0-5) - Hunting grounds, druid grove
- **Western Woods** (Cols 0-5) - Dangerous, bandits
- **Iron Mine** (6-10, 6-11) - Active mining operation
- **Pontar River** (Cols 26-31) - Major waterway
- **Southern Farmlands** (24-31) - Agriculture

### Key Locations

| Location | Coordinates | Room ID |
|----------|-------------|---------|
| Northern Gate | (10, 16) | #339 |
| Great Temple | (13, 11) | #430 |
| Royal Palace | (13, 21) | #440 |
| **Central Market** | **(18, 16)** | **#595** |
| Master Forge | (22, 12) | #719 |
| Harbor Master | (22, 22) | #729 |
| Iron Mine | (7, 8) | #235 |
| Druid Grove | (2, 15) | #82 |
| **Waystone** | **(-1, -1)** | **#12837** |

**Navigation Example**:
- From Northern Gate (10, 16) to Central Market (18, 16):
  - Go south 8 times → You're at Central Market

---

## NOVIGRAD (Large Free City)

**Grid**: 40x40 (1,600 rooms)
**Style**: Color-coded districts, largest city in the North
**Government**: Hierarch (theocratic rule)
**Special**: Each district has color-coded names for easy navigation

### Districts (Color-Coded)

1. **|yTemple District|n** (GOLD - Central)
   - Hierarch's absolute power
   - Temple Guards everywhere
   - Eternal Fire cathedral, religious oppression
   - Rows 13-22, Columns 21-30
   - **Recommended home**: Hierarch Square (17, 25)

2. **|cGildorf|n** (CYAN - NE)
   - Wealthy merchant quarter
   - Vivaldi Bank, auction houses
   - Private guards, immaculate streets
   - Rows 8-17, Columns 31-39

3. **|rThe Bits|n** (RED - NW)
   - Slums and poverty
   - Beggars, thieves, desperation
   - King of Beggars' territory
   - Rows 8-18, Columns 11-20

4. **|bHarborside|n** (BLUE - South)
   - Massive international port
   - Warehouses, docks, sailors
   - Harbormaster's Tower
   - Rows 28-39, Columns 0-39

5. **|mGlory Lane|n** (MAGENTA - East)
   - Entertainment and vice district
   - The Passiflora (exclusive brothel)
   - Gambling, music, pleasure
   - Rows 18-27, Columns 31-39

6. **|xPutrid Grove|n** (BLACK - West)
   - Cemetery district
   - Undertakers, graveyards
   - Ghoul-infested at night
   - Rows 13-22, Columns 0-10

7. **|gOxenfurt Gate|n** (GREEN - SW)
   - Trade route to university city
   - Scholars, bookshops, inns
   - Intellectual atmosphere
   - Rows 23-27, Columns 0-15

8. **|YTretogor Gate|n** (YELLOW - NW)
   - Redanian influence
   - Military presence despite free city status
   - Rows 8-12, Columns 0-10

### Surrounding Areas

- **Northern Swamps** (0-7) - Dangerous wetlands, will-o-wisps
- **Western Forests** (Cols 0-4) - Trade routes to Oxenfurt
- **Eastern Coast** (Cols 36-39) - Ocean shoreline

### Key Locations

| Location | Coordinates | Room ID | District |
|----------|-------------|---------|----------|
| **Hierarch Square** | **(17, 25)** | **#5700** | |yTemple|n |
| Eternal Fire Temple | (18, 26) | #5741 | |yTemple|n |
| Vivaldi Bank | (12, 35) | #5510 | |cGildorf|n |
| Auction House | (13, 36) | #TBD | |cGildorf|n |
| Kingfisher Inn | (14, 15) | #TBD | |rThe Bits|n |
| King of Beggars | (15, 16) | #5611 | |rThe Bits|n |
| Harbormaster | (33, 20) | #6335 | |bHarborside|n |
| Golden Sturgeon | (34, 18) | #TBD | |bHarborside|n |
| **The Passiflora** | (22, 35) | #5910 | |mGlory Lane|n |
| Rosemary & Thyme | (23, 34) | #TBD | |mGlory Lane|n |
| Cemetery Gate | (18, 5) | #TBD | |xPutrid Grove|n |
| Oxenfurt Gate | (27, 10) | #TBD | |gOxenfurt|n |
| Tretogor Gate | (10, 5) | #TBD | |YTretogor|n |
| **Waystone** | **(15, 0)** | **#5595** | Staff-Locked |

**Navigation Example**:
- From Hierarch Square (17, 25) to The Passiflora (22, 35):
  - Go south 5 times (17 → 22)
  - Go east 10 times (25 → 35)
  - You're at The Passiflora

---

## City Comparison

| Feature | Vengerberg | Novigrad |
|---------|------------|----------|
| **Size** | 1,024 rooms (32x32) | 1,600 rooms (40x40) |
| **Character** | Classic fantasy city | Dark medieval realism |
| **Government** | Royal palace | Hierarch (theocratic) |
| **Security** | Guards | Temple Guards |
| **Districts** | 5 | 8 (color-coded) |
| **Special** | Traditional wards | Color-coded names |
| **Commerce** | Market Ward | Multiple districts |
| **Religion** | Melitele-focused | Eternal Fire dominance |
| **Tone** | Hopeful | Oppressive |
| **Port** | River Ward | Massive Harborside |
| **Underworld** | Less prominent | King of Beggars |
| **Wealth Gap** | Moderate | Extreme (Gildorf vs Bits) |

---

## Travel Between Cities

### Waystone Teleportation (Staff Only)

**Requirements**: Builder permission level

**Locations**:
- **Vengerberg Waystone**: Room #12837 (northwest of city, special location)
- **Novigrad Waystone**: Room #5595 at coordinates (15, 0) in Putrid Grove

**Commands**:
- From Vengerberg: `activate waystone to novigrad` (or just `novigrad`)
- From Novigrad: `activate waystone to vengerberg` (or just `vengerberg`)

**Access Control**:
- Locked with: `traverse:perm(Builder)`
- Only staff/GMs can use
- Players cannot teleport between cities

**RP Justification**:
- Ancient magical waystones
- Rare and powerful artifacts
- Require authorization to activate
- Used for official business only

**For Player Travel** (future implementation):
- Implement caravan travel (multi-day journey)
- River barge routes
- Teleportation scrolls (expensive, rare)
- Quest rewards for fast travel unlocks

---

## Building New Cities

### Using the Builder Scripts

**Build Single City**:
```bash
python world/build_cities.py vengerberg
python world/build_cities.py novigrad
```

**Build Both Cities**:
```bash
python world/build_cities.py both
```

**Interactive Menu**:
```bash
python world/build_cities.py
# Follow on-screen prompts
```

### Individual Builder Scripts

**Vengerberg Only**:
```bash
python world/vengerberg_builder.py
```

**Novigrad Only**:
```bash
python world/novigrad_builder.py
```

---

## Database Information

**Current Database**: `server/evennia.db3`
**Size**: 9.7 MB
**Total Objects**: 12,800+ (rooms, exits, items, accounts)

**Breakdown**:
- Rooms: 2,626 (1,024 Vengerberg + 1,600 Novigrad + 2 bootstrap)
- Exits: 10,210
- Items: 40 (weapons, armor, shields)
- Other: Accounts, characters, organizations, etc.

---

## GM Tips

### Choosing Starting City

**Vengerberg** - Best for:
- Traditional fantasy campaigns
- Smaller, more manageable setting
- Focus on royal/political intrigue
- River trade themes
- Balanced tone

**Novigrad** - Best for:
- Dark, gritty campaigns
- Religious persecution themes
- Underworld/crime stories
- Massive scale, overwhelming city
- Social inequality themes
- Multiple distinct neighborhoods

### Cross-City Campaigns

**Quest Hooks**:
- Diplomatic missions between cities
- Trade route protection
- Fugitives fleeing between cities
- Investigation spanning both locations
- Religious conflicts (Melitele vs Eternal Fire)
- Criminal networks in both cities

**Using Waystones**:
- Reward for major quest completion
- Temporary access for urgent missions
- One-way tickets (must return normally)
- Plot device for time-sensitive scenarios

---

## Color Code Reference (Novigrad)

For districts with color-coded room names:

- **|y** = Yellow/Gold (Temple District)
- **|c** = Cyan (Gildorf)
- **|r** = Red (The Bits)
- **|b** = Blue (Harborside)
- **|m** = Magenta (Glory Lane)
- **|x** = Black/Dark (Putrid Grove)
- **|g** = Green (Oxenfurt Gate)
- **|Y** = Bright Yellow (Tretogor Gate)
- **|n** = Reset color

This helps players instantly identify which district they're in by looking at the room name color.

---

## Future Expansion Ideas

### Additional Cities

1. **Oxenfurt** - University city, scholarly focus
2. **Vizima** - Temeria's capital
3. **Tretogor** - Redania's capital
4. **Maribor** - Trade center
5. **Ard Carraigh** - Kaedwen's capital

### City Features to Add

- **Time system**: Day/night cycles affecting descriptions
- **Weather**: Rain, snow, fog
- **Events**: Festivals, markets, executions
- **NPCs**: Shopkeepers, guards, quest givers
- **Factions**: City-specific organizations
- **Dynamic economy**: Fluctuating prices
- **Crime system**: Wanted levels, guards
- **Housing**: Player-owned apartments
- **Reputation**: Standing in each district

---

## Quick Start for New Players

### Starting in Vengerberg (Recommended for New Players)

1. **Login** → Appears at Central Market Square (18, 16)
2. **Explore Market Ward**: Browse shops, talk to NPCs
3. **Visit Prancing Pony**: (18, 14) - Go west 2 times from market
4. **Check Craftsmen Quarter**: South to (22, 16), then west to forge
5. **Avoid dangerous areas**: Western woods, northern wilderness until ready

### Starting in Novigrad (Advanced Players)

1. **Login** → Appears at Hierarch Square (17, 25)
2. **Note your district**: Yellow color = Temple District
3. **Explore safely**: Temple District is safest (heavy guard presence)
4. **Avoid The Bits**: Red district is dangerous (pickpockets, violence)
5. **Visit Gildorf**: Cyan district for high-end shopping
6. **Check Glory Lane**: Magenta district for entertainment (watch yourself!)

---

## Navigation Tips

### Cardinal Directions

- **North** / **n**: Decreases row number (go up)
- **South** / **s**: Increases row number (go down)
- **East** / **e**: Increases column number (go right)
- **West** / **w**: Decreases column number (go left)

### Finding Coordinates

Each room stores coordinates in `db.coordinates` attribute.

**As player**: Look at room name - some show coordinates
**As builder**: Examine room with `@examine here`

### Distance Calculation

**Example**: From (10, 15) to (20, 25)
- Row difference: |20 - 10| = 10 (go south 10 times)
- Column difference: |25 - 15| = 10 (go east 10 times)
- Total moves: 20

---

## Commands Quick Reference

### Movement
- `north` / `n` - Move north
- `south` / `s` - Move south
- `east` / `e` - Move east
- `west` / `w` - Move west
- `look` / `l` - Look at current room

### Waystone (Staff Only)
- `activate waystone to vengerberg` - Teleport to Vengerberg
- `activate waystone to novigrad` - Teleport to Novigrad
- `vengerberg` - Shortcut alias
- `novigrad` - Shortcut alias

### Room Information
- `@examine here` - See room details (Builder)
- `look` - See room description
- `exits` - List available exits

---

## Conclusion

With two major cities fully realized, the Northern Kingdoms now offer:

- **2,626 unique locations** to explore
- **Diverse atmospheres** from hopeful to oppressive
- **Multiple campaign styles** supported
- **Hundreds of potential quest locations**
- **Rich worldbuilding** based on Witcher lore

Whether your players prefer Vengerberg's traditional fantasy or Novigrad's dark realism, both cities provide endless opportunities for adventure!

**Welcome to the Northern Kingdoms. Choose your city. Begin your legend.**

---

*For detailed city guides, see:*
- *VENGERBERG_CITY_GUIDE.md*
- *NOVIGRAD_CITY_GUIDE.md* (coming soon)

*For builder documentation, see:*
- *world/vengerberg_builder.py*
- *world/novigrad_builder.py*
- *world/build_cities.py*
