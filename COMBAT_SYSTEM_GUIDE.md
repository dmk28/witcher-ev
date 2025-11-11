# Witcher RPG Combat System Guide

## Overview

The Witcher RPG features a comprehensive turn-based combat system with:
- **Frame-based attack system** (Light/Standard/Heavy with recovery)
- **Three combat stances** (Defensive/Moderate/Offensive)
- **Two-turn spell casting** with concentration mechanics
- **Initiative-based turn order** (Reflexes + Perception + 1d10)
- **Racial combat modifiers** (Elf/Human/Dwarf)
- **Witcher fighting styles** (6 schools from Witcher 3)

---

## 🎮 Combat Commands

### Starting Combat

```
combat/start [<name>]
```

Starts a new combat encounter in the current room.

**Examples:**
```
combat/start Bandit Ambush
combat/start
```

**What happens:**
- Creates a combat encounter
- Automatically adds you as the first participant
- Rolls your initiative
- Other players can join with `combat/join`

### Joining Combat

```
combat/join
```

Join an active combat encounter in your current room.

**What happens:**
- Rolls initiative (Reflexes + Perception + 1d10)
- Calculates max HP (Endurance × 10)
- Sets starting stance to Moderate
- Places you in turn order

### Leaving Combat

```
combat/leave
```

Leave the current combat.

**Effects:**
- Removes you from combat
- Combat ends if only 1 or fewer combatants remain

### Ending Combat (GM)

```
combat/end
```

Forcibly end the combat (GM/Admin only).

---

## ⚔️ Attacking

### Basic Attack

```
attack <target>
```

Attack with a standard attack using blades.

**Examples:**
```
attack Bandit
attack Orc
attack Guard
```

### Attack with Type

```
attack <target> with <light|standard|heavy>
```

Specify attack type for tactical advantage.

**Attack Types:**

| Type | Recovery | Penalty | Damage | Best For |
|------|----------|---------|--------|----------|
| **Light** | 10 | 0 | -50% | Quick jabs, keeping pressure |
| **Standard** | 8 | -2 | Normal | Balanced approach |
| **Heavy** | 4 | -6 | +50% | Finishing blows, high damage |

**Examples:**
```
attack Bandit with light
attack Orc with heavy
attack Guard with standard
```

**Recovery Explained:**
- Higher recovery = less penalty next turn
- Recovery penalty applies to your NEXT action
- Light attacks let you act normally next turn
- Heavy attacks severely penalize your next turn (-6 dice!)

### Attack with Weapon Skill

```
attack <target> using <weapon skill>
attack <target> with <type> using <weapon skill>
```

Use a specific weapon skill for the attack.

**Weapon Skills:** blades, axes, maces, spears, crossbows, brawling

**Examples:**
```
attack Bandit using axes
attack Orc with heavy using maces
attack Guard with light using spears
```

---

## 🔮 Spellcasting

### Spellcasting Overview

Spells take **2 full turns** to cast:
1. **Turn 1**: Begin casting (`cast <difficulty> <element> at <target>`)
2. **Turn 2**: Continue concentrating (automatic)
3. **Turn 3**: Complete and release (`cast/complete <target>`)

**Important:**
- If you're HIT while casting, the spell is INTERRUPTED and lost!
- You must maintain concentration for 2 turns
- Sign Sorcery can only cast Easy and Moderate spells

### Begin Casting

```
cast <difficulty> <element> at <target>
```

**Spell Difficulties:**

| Difficulty | CR | Damage | Soak Limit | Cost |
|------------|-----|--------|------------|------|
| **Easy** | 10 | 1d10-2 | 1d10 | Low |
| **Moderate** | 15 | 2d10 | 1d10 | Medium |
| **Difficult** | 20 | 3d10 | 1d10 | High |
| **Elite** | 20+ | 5d10 | 1d10 | Very High |

**Elements:** fire, ice, lightning, earth, wind, arcane

**Examples:**
```
cast easy fire at Bandit
cast moderate ice at Orc
cast difficult lightning at Guard
cast elite arcane at Dragon
```

### Complete Spell

```
cast/complete <target>
```

Release a fully-charged spell (after 2 turns).

**Examples:**
```
cast/complete Bandit
cast/complete Dragon
```

### Racial Spell Modifiers

- **Elf**: -5 CR (easier to cast), but +20% damage taken
- **Human**: No modifiers
- **Dwarf**: +5 CR (harder to cast), but -20% damage taken

**Example:**
- Elf casting Moderate (15 CR): 15 - 5 = **10 CR** (much easier!)
- Dwarf casting Moderate (15 CR): 15 + 5 = **20 CR** (harder)

---

## 🛡️ Combat Stances

### Change Stance

```
stance <defensive|moderate|offensive>
```

**Stances:**

| Stance | Effect | Best For |
|--------|--------|----------|
| **Defensive** | +5 Reflexes for defense, +10 CR to attacks | Tanking, low HP |
| **Moderate** | Balanced, no modifiers | General combat |
| **Offensive** | +5 Agility for attacks, +10 CR to defense | High damage output |

**Examples:**
```
stance defensive   (when injured)
stance offensive   (when attacking)
stance moderate    (balanced approach)
```

**Tactical Use:**
- Start in **Moderate** for balance
- Switch to **Defensive** when low on HP
- Switch to **Offensive** when you need to finish an enemy quickly
- Defensive stance makes you harder to hit but your attacks are easier to dodge
- Offensive stance makes your attacks hit harder but you're easier to hit

---

## 📊 Combat Status

### View Combat

```
combatstatus
cs
```

Shows:
- All combatants in initiative order
- HP bars (color-coded: green/yellow/red)
- Current stance for each combatant
- Recovery penalties
- Spell casting status
- Current turn indicator
- Round number

**Example Output:**
```
======================================================================
                        Combat in Tavern
Round 3
======================================================================

>>> Geralt       [████████████░░░░░░░░] 60/100 Offensive (Recovery: -6)
    Bandit       [██████████████░░░░░░] 70/100 Moderate
    Yennefer     [████████████████████] 80/80  Defensive (Casting Fire: 1 turn)
    Orc          [███░░░░░░░░░░░░░░░░░] 15/120 Moderate

======================================================================
```

---

## ⚡ Combat Flow Example

### Complete Battle Walkthrough

**Setup:**
```
> combat/start Tavern Brawl
Combat started! Geralt joins with initiative 18, HP 80

> combat/join
Bandit joins combat! Initiative: 12, HP: 60
```

**Round 1 - Geralt's Turn (Initiative 18):**
```
> attack Bandit with heavy using blades
Geralt attacks Bandit with a heavy blades attack!
Attack roll: 45 vs Defense: 28
HIT!
Damage: 18 (Soaked: 3) = 15 damage dealt!
Bandit HP: 45/60

(Geralt now has -6 recovery penalty next turn from heavy attack)
```

**Round 1 - Bandit's Turn (Initiative 12):**
```
Bandit attacks Geralt!
Attack roll: 22 vs Defense: 35
MISS!
```

**Round 2 - Geralt's Turn:**
```
> stance defensive
Geralt shifts to defensive stance (+5 Reflexes defense, +10 CR to attacks)

(Recovery penalty of -6 applies to this action!)
```

**Round 2 - Bandit's Turn:**
```
Bandit attacks Geralt!
Attack roll: 28 vs Defense: 42  (Geralt's defensive stance helping!)
MISS!
```

**Round 3 - Geralt's Turn:**
```
> cast moderate fire at Bandit
Geralt begins casting a moderate fire spell!
(2 turns remaining)
```

**Round 4 - Geralt's Turn:**
```
Geralt's spell is ready! Use cast/complete <target>

> cast/complete Bandit
Geralt unleashes Moderate Fire at Bandit!
Spell roll: SUCCESS!
Damage: 15 (Soaked: 6) = 9 damage!
Bandit HP: 36/60
```

**Round 5 - Geralt's Turn:**
```
> stance offensive
Geralt shifts to offensive stance (+5 Agility attack, +10 CR to defense)

> attack Bandit with standard
Geralt attacks Bandit with a standard blades attack!
Attack roll: 42 vs Defense: 25
HIT!
Damage: 12 (Soaked: 2) = 10 damage dealt!
Bandit HP: 26/60
```

---

## 🐺 Witcher Combat Styles

If you're playing a Witcher, choose a fighting style for additional bonuses:

### Available Styles

| Style | Bonuses | Playstyle |
|-------|---------|-----------|
| **Cat** | +2 AGI, +1 REF | Fast attacks, dodging |
| **Viper** | +2 CUN, +1 AGI | Tactical, poisons |
| **Bear** | +2 STR, +2 END, -1 AGI | Tank, heavy armor |
| **Eagle** | +2 PER, +1 WIT | Tactical awareness |
| **Dragon** | +1 INT, +1 WIL, +1 PER | Sign magic mastery |
| **Basilisk** | +1 REF, +1 END, +1 WIT | Adaptable, versatile |

**Set in Admin Panel:**
- Navigate to Witcher Characters in admin
- Edit your character
- Select Witcher Style
- Bonuses automatically apply to stats

---

## 🎯 Combat Tactics & Strategy

### Attack Type Strategy

**Light Attacks:**
- Use when you need to attack every turn without penalty
- Good for wearing down enemies
- Perfect for maintaining offensive pressure
- Low risk, low reward

**Standard Attacks:**
- Balanced damage with manageable penalty
- Good general-purpose attack
- Moderate risk, moderate reward

**Heavy Attacks:**
- Use for finishing blows
- Devastating damage but leaves you vulnerable
- Only use when you can afford the -6 penalty
- High risk, high reward
- **Tip:** Use heavy attack, then switch to defensive stance next turn!

### Stance Strategy

**When to Use Defensive:**
- Low HP (under 50%)
- Facing multiple enemies
- Protecting someone
- Spell casters are targeting you

**When to Use Offensive:**
- High HP
- Need to finish an enemy quickly
- 1v1 combat with advantage
- Enemy is low on HP

**When to Use Moderate:**
- Start of combat
- Uncertain situations
- When balanced approach is best

### Spellcasting Strategy

**Spell Difficulty Choice:**
- **Easy**: Guaranteed hit, low damage - use for chip damage
- **Moderate**: Good balance - most common choice
- **Difficult**: High damage, moderate risk
- **Elite**: Devastating but risky - save for bosses

**Spell Timing:**
- Cast when protected (allies tanking)
- Cast from defensive stance (harder to hit)
- Never cast when enemy has high initiative (they'll interrupt you!)
- Cast after enemy uses heavy attack (they have -6 penalty to hit you)

**Spell Interruption:**
- If interrupted, spell is LOST
- Wasted 2 turns of actions
- Plan carefully!

### Racial Tactics

**Playing an Elf:**
- Leverage easy spell casting (-5 CR)
- Stay at range (you're fragile, +20% damage!)
- Use defensive stance more often
- Cast higher difficulty spells than others

**Playing a Dwarf:**
- Get in melee (you're sturdy, -20% damage!)
- Use offensive/moderate stances
- Rely on physical attacks over magic
- Tank for your party

**Playing a Human:**
- Most flexible
- Can adapt to any role
- No penalties or bonuses

---

## 📋 Quick Reference

### Combat Commands Cheat Sheet

```
combat/start [name]           - Start combat
combat/join                   - Join combat
combat/leave                  - Leave combat
combatstatus (cs)             - View combat state

attack <target>                                    - Standard attack with blades
attack <target> with <light|standard|heavy>        - Specific attack type
attack <target> using <weapon skill>               - Specific weapon
attack <target> with <type> using <skill>          - Both specified

cast <difficulty> <element> at <target>    - Begin casting (2 turns)
cast/complete <target>                     - Release charged spell

stance <defensive|moderate|offensive>      - Change stance
```

### Stats for Combat

- **HP**: Endurance × 10
- **Initiative**: Reflexes + Perception + 1d10
- **Attack Roll**: Agility + Weapon Skill (vs Reflexes + Weapon Skill)
- **Damage**: Strength + Weapon Skill × attack modifier
- **Soak**: Endurance + Resistance + Armor (vs attack CR)

### Important Numbers

**Attack Types:**
- Light: +0% damage, 0 penalty
- Standard: +0% damage, -2 penalty
- Heavy: +50% damage, -6 penalty

**Stances:**
- Defensive: +5 Reflexes defense, +10 CR to attacks
- Moderate: No modifiers
- Offensive: +5 Agility attack, +10 CR to defense

**Spell Difficulties:**
- Easy: 10 CR, 1d10-2 damage
- Moderate: 15 CR, 2d10 damage
- Difficult: 20 CR, 3d10 damage
- Elite: 20 CR, 5d10 damage

---

## 🔧 Technical Details

### Turn Order
1. Initiative is rolled once at combat start
2. Highest initiative goes first
3. Turn order stays the same each round
4. Spell casting advances automatically each turn

### Damage Calculation
1. Attack roll (contested)
2. If hit: Calculate base damage
3. Apply attack type modifier
4. Defender rolls soak
5. Apply racial damage modifier
6. Subtract from HP

### Spell Interruption
- Any damage interrupts casting
- Spell is lost completely
- Must start over from turn 1

### Recovery Penalties
- Applied on your NEXT action after attack
- Stacks with stance modifiers
- Affects all dice pools

---

## 🎭 Roleplay Tips

### Combat Emotes

Enhance combat with emotes:
```
> attack Bandit with heavy
> emote swings his silver sword in a wide arc!
>
> cast moderate fire at Orc
> emote channels flames in his palms, eyes glowing with power!
>
> stance defensive
> emote drops into a protective guard stance!
```

### Narrating Combat

Make combat cinematic:
- Describe your attacks
- React to hits and misses
- Narrate spell effects
- Show fear, determination, anger
- Celebrate victories, mourn defeats

---

## 🏆 Advanced Tactics

### Combo Strategies

**Heavy Attack + Defensive Stance:**
1. Heavy attack for big damage (-6 penalty)
2. Next turn: Switch to defensive (+5 Reflexes)
3. The +5 Reflexes helps offset your -6 penalty
4. Net result: -1 penalty but you hit hard and can defend

**Offensive Stance + Standard Attack:**
1. Switch to offensive (+5 Agility to attacks)
2. Use standard attacks consistently
3. Your attacks are more likely to hit
4. Accept the +10 CR to your defense

**Spell Casting + Defensive Stance:**
1. Switch to defensive stance
2. Begin casting spell
3. Harder for enemies to hit and interrupt you
4. Release spell safely

**Team Tactics:**
- Tanks use defensive stance, draw aggro
- Damage dealers use offensive stance
- Casters stay at range, protected by tanks
- Focus fire on single targets
- Interrupt enemy spellcasters!

---

## 📚 Example Characters

### Geralt - Witcher (Cat School)
- **Stats**: High AGI, REF (Cat bonuses)
- **Tactics**: Fast attacks, signs, dodging
- **Stance**: Offensive/Moderate
- **Attacks**: Light/Standard with blades
- **Magic**: Sign Sorcery (easy/moderate only)

### Yennefer - Sorceress (Elf)
- **Stats**: High INT, WIL
- **Tactics**: Devastating spells, stay at range
- **Stance**: Defensive (protect fragile elf)
- **Attacks**: Rarely melees
- **Magic**: Elite spells (Elf -5 CR makes them easier!)

### Yarpen - Dwarf Warrior
- **Stats**: High STR, END
- **Tactics**: Tank, heavy attacks, melee
- **Stance**: Offensive
- **Attacks**: Heavy with axes
- **Magic**: None (Dwarf +5 CR makes it too hard)

---

## 🐛 Troubleshooting

**"No active combat!"**
- Solution: Use `combat/start` to begin combat

**"You are not in combat!"**
- Solution: Use `combat/join` to join active combat

**"It's not your turn!"**
- Solution: Wait for your turn, use `combatstatus` to check order

**"You don't have access to magic!"**
- Solution: Your vocation doesn't allow Magery or Sign Sorcery
- Check your vocation's skill access in character sheet

**Spell was interrupted!**
- You were hit while casting
- Must start over with `cast ...` again

**Can't cast elite spell with Sign Sorcery!**
- Sign Sorcery limited to easy/moderate only
- Use Magery for difficult/elite spells

---

## 🎯 Final Tips

1. **Check combat status often** - `cs` is your friend
2. **Plan ahead** - Think about recovery penalties
3. **Protect casters** - They're vulnerable while casting
4. **Use stances tactically** - Don't stay in one stance all combat
5. **Heavy attacks are risky** - Use when you can afford the penalty
6. **Racial bonuses matter** - Elves cast, Dwarves fight
7. **Witcher styles are powerful** - Choose wisely
8. **Communication is key** - Coordinate with party
9. **Emote and roleplay** - Make combat cinematic
10. **Have fun!** - It's a game, enjoy the tactical depth

---

Built with Evennia 5.0.1
All combat code committed to `claude/witcher-game-setup-011CV1YXC76vUfTwMMushAkA`
For system documentation see: WITCHER_RPG_GUIDE.md
