# Social Combat / Intrigue System Guide

## Overview

The Intrigue system allows characters to engage in social combat using charm, cunning, appearance, and graces instead of physical combat stats. Victory allows converting social capital into material rewards such as gold, rare items, and favors.

**Examples from the Witcher World:**
- Dandelion seducing patronesses for gold and luxury accommodations
- Merchants negotiating better trade deals and prices
- Nobles intimidating commoners for information
- Courtesans manipulating targets for secrets and favors

## Core Mechanics

### Social Capital

Social Capital represents a character's standing and influence during the encounter. It functions like HP in physical combat.

**Formula:**
```
Base Social Capital = (Charm + Cunning + Appearance + Graces) × 5
Modified by Social Rank:
- Rank 1 (Outcast): ×0.8 (40 capital with 10 in each stat)
- Rank 2 (Commoner): ×1.0 (50 capital)
- Rank 3 (Knight): ×1.2 (60 capital)
- Rank 4 (Gentry): ×1.5 (75 capital)
- Rank 5 (Royalty): ×2.0 (100 capital)
```

When Social Capital reaches 0, the character is defeated socially.

### Initiative

Social combat uses **Wit + Perception** for initiative, representing mental quickness and the ability to read social cues.

### Social Rank Effects

Social rank affects encounters in two ways:

1. **Social Capital Multiplier** (see above)
2. **Difficulty Modifiers**: Each rank difference modifies CR by 5
   - Noble (Rank 5) vs Commoner (Rank 2) = -15 CR for noble (easier)
   - Outcast (Rank 1) vs Noble (Rank 5) = +20 CR for outcast (harder)

This represents the power dynamics of social hierarchy.

## Encounter Types

### Seduction
Use charm and appearance to win romantic/sexual favor.
- **Best Stats**: Appearance, Charm
- **Best Vocations**: Courtesan, Bard
- **Available Actions**: Seduce, Charm, Flatter

### Negotiation
Use cunning and graces to make deals and trade.
- **Best Stats**: Cunning, Graces
- **Best Vocations**: Merchant, Noble
- **Available Actions**: Manipulate, Charm, Argue

### Intimidation
Use presence to cow opponents into submission.
- **Best Stats**: Charm (as presence), Cunning
- **Best Vocations**: Soldier, Knight, Witcher
- **Available Actions**: Intimidate, Threaten

### Debate
Use wit and logic to win arguments.
- **Best Stats**: Cunning
- **Best Vocations**: Sorcerer, Noble
- **Available Actions**: Argue, Manipulate

### Manipulation
Use cunning to trick and control perspectives.
- **Best Stats**: Cunning, Graces
- **Best Vocations**: Infiltrator, Courtesan
- **Available Actions**: Manipulate, Deceive, Undermine

## Stances

Your stance affects which actions are available and provides bonuses to certain stats.

### Charming Stance
"Emphasize appeal and likability"
- **Bonuses**: +2d to Charm actions, +1d to Appearance actions
- **Best For**: Seduction, friendly negotiations
- **Available Actions**: Charm, Seduce, Flatter, Rally

### Cunning Stance
"Use wit and manipulation"
- **Bonuses**: +2d to Cunning actions, +1d to Graces actions
- **Best For**: Manipulation, debate
- **Available Actions**: Manipulate, Deceive, Argue, Prepare

### Bold Stance
"Direct and assertive approach"
- **Bonuses**: +1d to Charm actions, -5 CR on Cunning actions
- **Best For**: Intimidation, aggressive negotiation
- **Available Actions**: Intimidate, Threaten, Charm, Argue

### Subtle Stance
"Indirect and measured"
- **Bonuses**: +2d to Graces actions, +1d to Cunning actions
- **Best For**: Careful manipulation, composed debate
- **Available Actions**: Flatter, Undermine, Compose, Prepare

## Social Actions

### Attack Actions
Directly reduce opponent's social capital.

#### Charm (Charm)
- **Stance**: Charming, Bold
- **CR**: 20
- **Damage**: 3d10
- Use natural charisma to win favor

#### Seduce (Appearance + Charm)
- **Stance**: Charming
- **CR**: 25
- **Damage**: 4d10
- **Encounter**: Seduction only
- Use appearance and charm to captivate romantically

#### Flatter (Graces + Appearance)
- **Stance**: Charming, Subtle
- **CR**: 18
- **Damage**: 2d10
- Use graceful compliments to please

#### Manipulate (Cunning)
- **Stance**: Cunning, Subtle
- **CR**: 22
- **Damage**: 3d10
- Use cunning to trick and control perspectives

#### Deceive (Cunning + Charm)
- **Stance**: Cunning, Bold
- **CR**: 24
- **Damage**: 3d10
- Lie convincingly

#### Intimidate (Charm + Cunning)
- **Stance**: Bold
- **CR**: 20
- **Damage**: 3d10
- Cow opponent with presence

#### Threaten (Cunning + Charm)
- **Stance**: Bold
- **CR**: 22
- **Damage**: 4d10
- **Encounter**: Intimidation only
- Make bold threats to break their will

#### Argue (Cunning)
- **Stance**: Bold, Cunning
- **CR**: 20
- **Damage**: 3d10
- Use logical arguments in debate

### Support Actions
Restore social capital (yours or an ally's).

#### Compose (Graces)
- **Stance**: Subtle
- **CR**: 15
- Regain composure and restore social capital

#### Rally (Charm)
- **Stance**: Charming, Bold
- **CR**: 18
- Bolster morale and restore social capital

### Undermine Actions
Apply ongoing penalties to opponent.

#### Undermine (Cunning + Graces)
- **Stance**: Subtle, Cunning
- **CR**: 20
- **Damage**: 2d10
- **Effect**: +5 CR penalty for 3 rounds
- Subtly weaken the target's position

### Boost Actions
Apply bonuses to self or ally.

#### Prepare (Cunning)
- **Stance**: Subtle, Cunning
- **CR**: 15
- **Effect**: +2d bonus for 1 round
- Set up your next move

## Defensive Stats

Each attacking stat is opposed by a defensive stat:

- **Charm** vs **Cunning** (see through charm with wit)
- **Cunning** vs **Graces** (grace deflects manipulation)
- **Appearance** vs **Graces** (social grace resists appearance)
- **Graces** vs **Charm** (charm overcomes formality)

The defender's stat adds to the difficulty:
```
Final CR = Base CR + (Defender's Stat / 2) + Rank Modifier
```

## Rewards System

Upon defeating an opponent, rewards are calculated based on:

1. **Victory Margin**: Winner's remaining social capital
2. **Opponent's Wealth Level** (1-7)

### Wealth Levels

| Level | Status | Gold Range |
|-------|--------|------------|
| 1 | Destitute | 10-50 crowns |
| 2 | Poor | 50-200 crowns |
| 3 | Common | 200-1000 crowns |
| 4 | Wealthy | 1000-5000 crowns |
| 5 | Rich | 5000-20000 crowns |
| 6 | Noble | 20000-100000 crowns |
| 7 | Royalty | 100000+ crowns |

### Reward Calculation

**Gold Reward:**
```
Victory Margin 0-20: 10-30% of wealth range
Victory Margin 21-50: 30-50% of wealth range
Victory Margin 51+: 50-80% of wealth range
```

**Item Rewards:**
- Wealth 4+ & Margin 30+: Common luxury item
- Wealth 5+ & Margin 50+: Rare luxury item
- Wealth 6+ & Margin 70+: Noble gift item

**Favor Rewards:**
- Favor Level = Victory Margin / 25 (max 3)

### Example Scenarios

#### Dandelion Seducing a Duchess
- **Duchess**: Social Rank 4 (Gentry), Wealth 6 (Noble)
- **Dandelion**: Courtesan vocation, strong Charm & Appearance
- **Victory Margin**: 45 social capital remaining
- **Rewards**:
  - Gold: ~30000 crowns (40% of 50000-70000 range)
  - Item: Common luxury item (perfume, jewelry)
  - Favor: Level 1 favor (introduction to court)

#### Merchant Negotiating Prices
- **Wealthy Trader**: Social Rank 3, Wealth 4 (Wealthy)
- **Merchant PC**: Strong Cunning & Graces
- **Victory Margin**: 25 social capital
- **Rewards**:
  - Gold: ~1200 crowns (40% of 3000 avg)
  - Favor: Level 1 (better ongoing prices)

## Commands

### Starting an Encounter

```
intrigue <target> [type] [stakes]
seduce <target> [stakes]
negotiate <target> [stakes]
intimidate <target> [stakes]
```

**Examples:**
```
seduce Duchess Anna "expensive gift and introduction"
negotiate Merchant Zdenek "better prices on alchemy ingredients"
intimidate Guard "information about the baron's plans"
```

### During Combat

```
social <action> <target>     - Perform a social action
social list                   - List available actions
socialstance <stance>         - Change your stance
socialstatus                  - View encounter status
```

**Examples:**
```
social charm duchess
social seduce anna
social undermine lord
socialstance subtle
```

### Changing Stance

```
socialstance charming    - Emphasize appeal (+2d Charm)
socialstance cunning     - Use manipulation (+2d Cunning)
socialstance bold        - Direct approach (+1d Charm, -5 CR Cunning)
socialstance subtle      - Measured approach (+2d Graces)
```

## Strategic Tips

### For Seduction (Dandelion Style)
1. Start in **Charming** stance
2. Use **Flatter** early to build momentum
3. Switch to **Seduce** for the finishing blow
4. Higher Appearance and Charm stats are crucial
5. Target high-wealth, lower-rank opponents for best rewards

### For Negotiation
1. Use **Cunning** stance
2. **Manipulate** to control the conversation
3. **Prepare** before big moves for bonus dice
4. Use **Undermine** to weaken their position over time

### For Intimidation
1. **Bold** stance is essential
2. **Intimidate** early to establish dominance
3. Social rank advantage helps significantly
4. Works best against lower-rank targets

### Vocation Synergies

**Courtesan**: Natural seduction masters
- High Appearance and Charm
- Vocation bonuses to social stats
- Best for seduction and manipulation

**Noble**: Negotiation and debate experts
- High social rank (3-4) gives CR advantages
- Leadership skill adds presence
- Best for negotiation and intimidation

**Merchant**: Trade negotiation specialists
- Cunning-focused build
- Best for negotiation encounters
- Can convert victories into trade advantages

**Infiltrator**: Subtle manipulation
- High Cunning
- Best for subtle manipulation
- Use Undermine and Deceive

**Witcher**: Social disadvantage (Rank 1-2)
- +5 to +10 CR penalty in most encounters
- Intimidation is their best social option
- Should avoid seduction unless high Appearance compensates

## Game Balance

### Why Witchers Are Socially Stunted

Witchers face significant social combat disadvantages:
- **Social Rank 1-2**: +5 to +10 CR penalty
- **Mutations**: Strange appearance (though +3 for seduction vs females)
- **Reputation**: Feared and mistrusted

This balances their combat superiority. A legendary bladesman at Rank 3-4 can excel in both physical and social combat, representing characters like noble duelists in the books.

### Converting Social Success to Gameplay

Social combat victories provide:
- **Gold**: Direct currency gain
- **Items**: Luxury goods, rare consumables
- **Favors**: Quest hooks, access to restricted areas, better prices

This makes social characters viable without requiring them to fight monsters.
