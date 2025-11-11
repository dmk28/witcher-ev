# Witcher RPG System Guide

## Overview

This Evennia game implements a complete Witcher universe RPG system with:
- **11 Vocations** with unique abilities and bonuses
- **12 Core Stats** across Physical, Mental, and Social categories
- **Exploding d10 Dice System** where 10s roll d100 and add to the total
- **Model-Driven Architecture** for easy character management via Django admin
- **Comprehensive Skill System** including combat, magic, crafting, and more

---

## System Architecture

### Model → Typeclass Pattern

This system follows Evennia best practices with a model → typeclass pattern:

- **Models** (`world/witcher_rpg/models.py`) - Store all character data
- **Typeclasses** (`typeclasses/characters.py`) - Provide behavior and methods
- **Admin Panels** (`world/witcher_rpg/admin.py`) - Intuitive management interface

### Key Components

1. **Vocation Model** - 11 character vocations with stat modifiers
2. **VocationFeat Model** - Special abilities tied to each vocation
3. **CharacterStats Model** - 12 core stats for characters
4. **CharacterSkills Model** - Combat, special, and general skills
5. **WitcherCharacter Model** - Main character data container
6. **WitcherCharacter Typeclass** - In-game character behavior

---

## The 11 Vocations

### 1. **Soldier**
- **Bonuses**: +2 Strength, +1 Endurance
- **Feat**: Martial Training (+2d to Strength)
- **Description**: Trained warriors and military personnel

### 2. **Bladesman**
- **Bonuses**: +2 Agility, +1 Reflexes
- **Feat**: Master of the Sword (+2d to Agility with blades)
- **Description**: Master swordsmen dedicated to the blade

### 3. **Knight**
- **Bonuses**: +1 Strength, +1 Endurance, +1 Willpower
- **Feat**: Armored Combat (+2d to Endurance on defense)
- **Access**: Crafting
- **Description**: Armored warriors sworn to honor

### 4. **Inquisitor**
- **Bonuses**: +2 Willpower, +1 Perception, +1 Cunning
- **Feat**: Zealous Conviction (+2d to Willpower)
- **Access**: Crafting
- **Description**: Religious enforcers who hunt heretics

### 5. **Sorcerer/ess**
- **Bonuses**: +2 Intelligence, +1 Graces, +1 Willpower
- **Feat**: Arcane Mastery (+2d to Intelligence for magic)
- **Access**: Alchemy, Magery, Crafting
- **Description**: Wielders of arcane magic

### 6. **Witcher**
- **Bonuses**: +1 Reflexes, +1 Agility, +1 Endurance
- **Penalties**: -2 Graces
- **Special**: +3 Appearance for seduction rolls vs females (lore-accurate)
- **Feat**: Witcher Mutations (+1d to Reflexes)
- **Access**: Alchemy, Sign Sorcery, Crafting
- **Description**: Mutated monster hunters with supernatural abilities. Despite visible mutations (cat eyes, pale skin), Witchers possess an inexplicable allure to women.

### 7. **Courtesan**
- **Bonuses**: +2 Charm, +1 Appearance, +1 Cunning, +1 Graces
- **Feat**: Silver Tongue (+2d to Charm)
- **Description**: Masters of social manipulation

### 8. **Infiltrator**
- **Bonuses**: +1 Agility, +1 Reflexes, +2 Cunning, +1 Perception
- **Feat**: Shadow Walker (+2d to Cunning for stealth)
- **Access**: Alchemy
- **Description**: Spies, thieves, and assassins

### 9. **Noble**
- **Bonuses**: +2 Graces, +1 Charm, +1 Intelligence
- **Feat**: Noble Bearing (+2d to Graces)
- **Description**: Highborn leaders trained in courtly arts

### 10. **Alchemist**
- **Bonuses**: +2 Intelligence, +1 Wit, +1 Perception
- **Feat**: Chemical Expertise (+2d to Intelligence for alchemy)
- **Access**: Alchemy, Crafting
- **Description**: Masters of potions and elixirs

### 11. **Merchant**
- **Bonuses**: +2 Cunning, +1 Charm, +1 Wit
- **Feat**: Deal Maker (+2d to Cunning for trading)
- **Description**: Expert negotiators and traders

---

## The 12 Stats

### Physical Stats
- **Strength (STR)** - Physical power and melee damage
- **Agility (AGI)** - Speed, dodging, and finesse
- **Endurance (END)** - Stamina, health, and resistance
- **Reflexes (REF)** - Reaction speed and initiative

### Mental Stats
- **Wit (WIT)** - Quick thinking and cleverness
- **Intelligence (INT)** - Knowledge and reasoning
- **Willpower (WIL)** - Mental fortitude and magic power
- **Perception (PER)** - Awareness and noticing details

### Social Stats
- **Charm (CHA)** - Charisma and likability
- **Appearance (APP)** - Physical attractiveness
- **Graces (GRA)** - Social grace and etiquette
- **Cunning (CUN)** - Deception and manipulation

---

## Skills System

### Combat Skills
- **Blades** - Swords and bladed weapons
- **Axes** - Axes and chopping weapons
- **Maces** - Maces and blunt weapons
- **Spears** - Spears and polearms
- **Crossbows** - Crossbows and ranged weapons
- **Brawling** - Unarmed combat

### Special Skills (Require Vocation Access)
- **Alchemy** - Potion-making and alchemical knowledge
- **Magery** - Spell-casting ability
- **Sign Sorcery** - Witcher sign magic

### Crafting Skills (Choose One Specialization)
- **Smithing** - Metalworking and weapon/armor crafting
- **Carpentry** - Woodworking and construction
- **Herbalism** - Plant lore and herbal remedies

### General Skills
- **Athletics** - Physical fitness, running, jumping, climbing

---

## Dice System

### Exploding d10 Mechanics

1. **Basic Roll**: Roll a 10-sided die (d10)
2. **Explosion**: If you roll a 10, roll d100 and add 10 to get a result of 11-110
3. **Multiple Dice**: Each die can explode independently

### Examples

```
Roll 3d10:
- Die 1: 7 (no explosion)
- Die 2: 10 → rolls d100 → 45 → result: 55 (exploded!)
- Die 3: 4 (no explosion)
Total: 7 + 55 + 4 = 66
```

### Challenge Types

#### Fixed Difficulty Check
- Roll dice pool vs. target number
- Meet or exceed to succeed
- Example: Roll 5d10 vs. difficulty 30

#### Contested Check
- Two parties roll opposed checks
- Highest total wins
- Example: Attacker rolls 4d10, Defender rolls 3d10

---

## Using the Admin Panel

### Accessing Admin

1. Start the Evennia server: `evennia start`
2. Create a superuser: `evennia createsuperuser`
3. Access admin at: `http://localhost:4001/admin/`

### Managing Vocations

Navigate to: **Witcher RPG → Vocations**

- View all vocations and their stat modifiers
- Edit bonuses/penalties for each vocation
- Manage vocation feats inline
- Toggle skill access (Alchemy, Magery, etc.)

### Creating a Character

1. Go to **Witcher RPG → Witcher Characters**
2. Click "Add Witcher Character"
3. Select:
   - DB Object (the Evennia character object)
   - Character name
   - Vocation
   - Nation (optional)
4. The system auto-creates CharacterStats and CharacterSkills
5. Edit stats and skills as needed

### Viewing Effective Stats

In the character admin, expand "Effective Stats (with Vocation bonuses)" to see:
- Base stats + vocation modifiers
- All stats displayed in organized groups

---

## In-Game Usage

### Character Typeclass Methods

The `WitcherCharacter` typeclass (in `typeclasses/characters.py`) provides:

#### Get Stats and Skills
```python
char.get_stat('strength')  # Returns effective strength (base + vocation bonus)
char.get_skill('blades')   # Returns blade skill level
char.has_skill_access('alchemy')  # Check if vocation allows alchemy
```

#### Calculate Dice Pool
```python
# Stat only
dice = char.calculate_dice_pool('strength')

# Stat + Skill
dice = char.calculate_dice_pool('agility', 'blades')

# With bonus dice
dice = char.calculate_dice_pool('strength', bonus_dice=2)
```

#### Perform Rolls
```python
# Simple roll
result = char.roll_check('strength')

# Skill check
result = char.roll_check('agility', 'blades')

# vs Difficulty
result = char.roll_check('intelligence', 'alchemy', difficulty=25)

# Show to room
result = char.roll_check('strength', show_to_room=True)
```

#### Display Character Sheet
```python
sheet = char.display_sheet()  # Returns formatted character sheet
```

### Using the Dice System Directly

```python
from world.witcher_rpg.dice import DiceRoller, ChallengeResolver

# Roll multiple d10s
result = DiceRoller.roll_multiple_d10(5)
# result = {
#     'rolls': [7, 55, 4, 10, 23],  # 55 and 23 exploded
#     'total': 99,
#     'explosions': 2,
#     'details': [...]
# }

# Fixed difficulty check
result = ChallengeResolver.fixed_difficulty_check(
    num_dice=5,
    difficulty=30
)

# Contested check
result = ChallengeResolver.contested_check(
    attacker_dice=4,
    defender_dice=3
)
```

---

## File Structure

```
witcher-ev/
├── world/
│   └── witcher_rpg/           # Custom Witcher RPG app
│       ├── models.py          # Django models for characters, stats, vocations
│       ├── admin.py           # Admin panel configuration
│       ├── dice.py            # Dice rolling system
│       └── migrations/
│           ├── 0001_initial.py
│           └── 0002_populate_vocations.py  # Populates default vocations
│
├── typeclasses/
│   └── characters.py          # WitcherCharacter typeclass with game behavior
│
└── server/
    └── conf/
        └── settings.py        # Evennia settings (includes witcher_rpg app)
```

---

## Next Steps

### 1. Start the Server
```bash
evennia migrate  # Already done
evennia start
```

### 2. Create a Superuser
```bash
evennia createsuperuser
```

### 3. Access Admin Panel
Visit `http://localhost:4001/admin/`

### 4. Create Characters
- Use admin panel to create WitcherCharacter objects
- Set stats, skills, and vocation
- Characters automatically get vocation bonuses

### 5. Customize Vocations
- Edit vocations in admin panel
- Add/modify feats
- Adjust stat modifiers

### 6. Build the World
- Create rooms, NPCs, and items
- Use the dice system for skill checks
- Implement combat commands using the roll system

---

## Example Character Creation Workflow

1. **Create base Evennia character object** (via @charcreate or admin)
2. **Create WitcherCharacter in admin**:
   - Link to Evennia object
   - Choose vocation (e.g., "Witcher")
   - Set character name
3. **Set base stats** (1-10 range):
   - Physical: STR:5, AGI:6, END:6, REF:7
   - Mental: WIT:5, INT:4, WIL:5, PER:6
   - Social: CHA:3, APP:4, GRA:2, CUN:5
4. **Effective stats** (with Witcher bonuses):
   - AGI: 6+1=7, REF: 7+1=8, END: 6+1=7
   - GRA: 2-2=0, APP: 4-1=3
5. **Set skills**:
   - Blades: 6, Alchemy: 4, Sign Sorcery: 3, Athletics: 4
6. **Result**: A mutated monster hunter with enhanced reflexes, skilled with blades, but socially awkward

---

## Tips and Best Practices

1. **Use Admin for Management**: The admin panel is the easiest way to create and modify characters
2. **Vocation Matters**: Choose vocations carefully - they significantly impact character capabilities
3. **Exploding Dice**: Remember that 10s can create dramatically high results
4. **Skill Access**: Check vocation skill access before training restricted skills
5. **Effective Stats**: Always use `get_stat()` to account for vocation bonuses

---

## Customization

### Adding New Vocations

1. Go to admin: **Witcher RPG → Vocations → Add Vocation**
2. Set stat modifiers
3. Toggle skill access
4. Add feats inline

### Modifying Existing Feats

1. Go to admin: **Witcher RPG → Vocation Feats**
2. Find the feat to modify
3. Adjust bonus dice, stat, or trigger condition

### Creating Custom Dice Mechanics

Edit `world/witcher_rpg/dice.py` to add:
- New dice types
- Different explosion mechanics
- Custom challenge resolvers

---

## Technical Notes

- **Evennia Version**: 5.0.1
- **Django Version**: 5.2.8
- **Python Version**: 3.11.14
- **Database**: SQLite (default) - ready for PostgreSQL migration
- **Model Pattern**: OneToOne relationships for stats/skills
- **Admin Optimization**: Uses `list_select_related` for query efficiency

---

## Troubleshooting

### Character Not Showing Stats
- Ensure WitcherCharacter object is created in admin
- Check that stats and skills objects are linked
- Verify vocation is selected

### Skill Access Issues
- Check vocation's skill access flags in admin
- Witcher: Has Alchemy, Sign Sorcery
- Sorcerer: Has Alchemy, Magery, Crafting
- Others: Check individual vocation settings

### Dice Not Exploding
- Verify using `DiceRoller.roll_exploding_d10()` or `roll_multiple_d10()`
- Check roll details in result dictionary

---

## Support and Documentation

- **Evennia Docs**: https://www.evennia.com/docs/
- **Django Admin**: https://docs.djangoproject.com/en/stable/ref/contrib/admin/
- **Witcher Universe**: https://witcher.fandom.com/

---

Built with Evennia 5.0.1 and Django 5.2.8
Model → Typeclass architecture for maximum flexibility
All code committed and pushed to `claude/witcher-game-setup-011CV1YXC76vUfTwMMushAkA`
