# Shop System Guide

## Overview

The shop system allows players to buy and sell items through NPC-run shops. Players can also own shops, and merchants are susceptible to social combat for better prices.

**Key Features:**
- 8 shop types (weaponsmith, alchemist, jeweler, etc.)
- 4 tier levels determining quality and gold reserves
- Faction-based inventory restrictions
- Automatic restocking based on rules
- Social combat integration (haggling for discounts)
- Player ownership and management

## Shop Types

### Weaponsmith
- **Sells**: Swords, axes, crossbows, polearms
- **Buys**: Weapons
- **Best For**: Combat-focused characters

### Armorsmith
- **Sells**: Armor, protective gear, shields
- **Buys**: Armor
- **Best For**: Tanks and knights

### Jeweler
- **Sells**: Jewelry, gems, luxury items
- **Buys**: Jewelry, gems, luxury goods
- **Best For**: Wealthy patrons, nobles

### Alchemist
- **Sells**: Potions, oils, alchemical ingredients
- **Buys**: Potions, ingredients, oils
- **Best For**: Witchers, sorcerers

### General Store
- **Sells**: Basic supplies, consumables, materials
- **Buys**: Almost anything
- **Best For**: Common folk, travelers

### Tailor
- **Sells**: Clothing, fashion items
- **Buys**: Clothing, luxury fabrics
- **Best For**: Nobles, courtesans

### Blacksmith
- **Sells**: Tools, basic weapons, materials
- **Buys**: Weapons, armor, tools, materials
- **Best For**: Crafters, common soldiers

### Enchanter
- **Sells**: Scrolls, runes, magical items
- **Buys**: Magic items, scrolls, runes
- **Best For**: Mages, sorcerers

## Shop Tiers

### Tier I - Poor Quality
- **Gold Reserves**: 500 crowns
- **Inventory**: 3-8 items
- **Quality**: Basic, low-tier items only
- **Typical Location**: Villages, poor districts

### Tier II - Common Quality
- **Gold Reserves**: 2,000 crowns
- **Inventory**: 8-15 items
- **Quality**: Common items, some tier II
- **Typical Location**: Towns, city outskirts

### Tier III - Good Quality
- **Gold Reserves**: 10,000 crowns
- **Inventory**: 15-25 items
- **Quality**: Good selection, tier III items
- **Typical Location**: Cities, wealthy districts

### Tier IV - Excellent Quality
- **Gold Reserves**: 50,000 crowns
- **Inventory**: 25-40 items
- **Quality**: Rare items, tier IV equipment
- **Typical Location**: Capital cities, noble quarters

## Factions

Shops can be affiliated with factions, affecting available inventory:

- **Independent**: No restrictions
- **Nilfgaard**: Imperial weapons, Nilfgaardian styles
- **Temeria**: Northern Kingdom goods
- **Redania**: Redanian specialties
- **Skellige**: Nordic/Viking inspired items
- **Witcher Guild**: Witcher gear, special potions
- **Mage Conclave**: Magical items, scrolls
- **Merchant Guild**: Wide variety, best prices

## Commands

### Browse
```
browse
list
shop
wares
```
View all items available in the current shop, including:
- Item names
- Quantities in stock
- Prices
- Tiers (★ symbols)
- Special items marked with *

### Buy
```
buy <item> [quantity]
buy sword
buy potion 3
```
Purchase items from the shop. If you have a discount from social combat, it's automatically applied.

**Requirements:**
- Sufficient gold
- Item in stock
- Shop is open

### Sell
```
sell <item> [quantity]
sell sword
sell potion 2
```
Sell items from your inventory to the shop.

**Factors Affecting Price:**
- Item condition (damaged = less gold)
- Shop type (must accept that item type)
- Shop's gold reserves
- Social combat bonus (if any)

### Haggle
```
haggle
negotiate
bargain
```
Start social combat with the merchant for better prices.

**Victory Results:**
- Small (1-20 capital): 5-15% discount
- Medium (21-40): 15-30% discount
- Large (41+): 30-50% discount

Discount applies to your NEXT transaction (buy or sell) at that shop.

### Shop Management (Owners Only)
```
shopmanage
shopmanage restock
shopmanage prices <markup%> <buyback%>
shopmanage open
shopmanage close
```

Owner commands for managing your shop:
- **restock**: Force immediate restock
- **prices**: Adjust markup (100-500%) and buyback (10-100%)
- **open/close**: Toggle shop status
- **(no args)**: View detailed shop status

## Pricing System

### Markup (Sell Prices)
Default: 150% (50% markup on base value)

**Formula:**
```
Sell Price = Base Value × (Markup % / 100)
```

**Example:**
- Base Value: 1000 crowns
- Markup: 150%
- Sell Price: 1500 crowns

### Buyback (Purchase Prices)
Default: 50% (shop pays half the base value)

**Formula:**
```
Buy Price = Base Value × (Buyback % / 100) × (Condition % / 100)
```

**Example:**
- Base Value: 1000 crowns
- Buyback: 50%
- Condition: 80%
- Buy Price: 400 crowns

## Restocking System

Shops automatically restock every 24 hours (configurable).

### Restocking Rules

Rules define what items can appear based on:
1. **Shop Type**: Weaponsmiths get weapons, alchemists get potions
2. **Tier Range**: Higher tiers get better items
3. **Stock Chance**: Percentage chance item appears (0-100%)
4. **Quantity Range**: Min-max items to stock
5. **Faction Restrictions**: Some items exclusive to factions

### Example Restock Rule
```python
# Steel Sword in Weaponsmith
- Shop Type: weaponsmith
- Min Tier: 2
- Max Tier: 4
- Stock Chance: 60%
- Min Quantity: 1
- Max Quantity: 3
- Allowed Factions: (none = all)
- Restricted Factions: ['witcher']  # Witchers don't sell common swords
```

### Manual Restocking
Shop owners can force restock with:
```
shopmanage restock
```

## Social Combat Integration

### Haggling Process

1. **Enter shop with merchant NPC**
2. **Use `haggle` command**
3. **Engage in negotiation-type social combat**
4. **Use social actions** (Manipulate, Charm, Argue, etc.)
5. **Defeat merchant** by reducing their social capital to 0
6. **Receive discount** based on victory margin

### Discount Application

Discounts are stored temporarily (in `character.ndb.shop_discount`) and apply to the NEXT transaction only.

**After winning haggle:**
```
> haggle
[Social combat occurs]
You've successfully negotiated a 35% discount at The Steel & Silver!
Use 'buy' or 'sell' now to apply your discount!

> buy sword
You purchase 1x Steel Sword for 975 crowns (35% discount!)
```

### Strategic Tips

**For Buyers:**
- Haggle BEFORE buying expensive items
- Use Cunning-based builds (merchants defend with Graces)
- Bold stance works well for intimidation
- Higher social rank = easier negotiation

**For Sellers:**
- Haggle to get bonuses on sale prices
- Repair items before selling (better condition = more gold)
- Sell to appropriate shops (weaponsmith pays more for weapons)

## Shop Ownership

### Acquiring a Shop

Shops can be assigned to players through:
1. **Admin**: Set owner field in Django admin
2. **In-game events**: Rewards, purchases, quests
3. **Mission rewards**: Complete merchant guild missions

### Owner Benefits

- **Profit**: Keep all gold from player transactions
- **Control prices**: Adjust markup and buyback percentages
- **Manage inventory**: Force restocks, add special items
- **Control access**: Open/close shop as needed

### Owner Responsibilities

- **Maintain gold reserves**: Shop needs gold to buy from players
- **Stock management**: Ensure good inventory
- **Merchant management**: Assign NPC merchant
- **Pricing balance**: Fair prices attract customers

## Advanced Features

### Special Items

Items marked `is_special=True` in inventory:
- Don't disappear when quantity reaches 0
- Don't restock automatically
- Usually player-sold items or unique goods
- Can be priced differently

### Transaction Logging

All transactions are logged with:
- Customer name
- Item and quantity
- Prices
- Social combat discount/bonus
- Timestamp

Owners can view recent transactions with `shopmanage`.

### Faction-Based Inventory

Examples of faction restrictions:

**Witcher Guild Shop:**
- Stocks witcher-specific potions
- Stocks silver swords
- Doesn't stock common weapons
- Higher prices but specialized goods

**Nilfgaardian Armory:**
- Imperial weapons and armor
- Restricted from stocking Northern Kingdom items
- Nilfgaardian style aesthetics

**Independent General Store:**
- No restrictions
- Widest variety
- Good for common goods

## Example Scenarios

### Scenario 1: Buying a Sword
```
> browse
The Steel & Silver - Weaponsmith
Tier 3 | Independent
Merchant: Marcus the Smith

Item                           Qty   Price      Tier
----------------------------------------------------------------------
Iron Sword                     5     150        ★
Steel Sword                    2     1500       ★★
Silver Sword                   1     5000       ★★★

> buy steel sword
You purchase 1x Steel Sword for 1500 crowns.
Remaining gold: 3500 crowns
```

### Scenario 2: Haggling and Buying
```
> haggle
Marcus the Smith begins negotiation with you!
[Initiative order shown]

> social manipulate marcus
[Social combat ensues...]

Social Encounter Complete!
You have emerged victorious!
=== Haggling Success! ===
You've successfully negotiated a 25% discount at The Steel & Silver!

> buy silver sword
You purchase 1x Silver Sword for 3750 crowns (25% discount!)
Remaining gold: 2250 crowns
```

### Scenario 3: Selling Loot
```
> inv
You are carrying:
  Damaged Iron Sword (60% condition)
  Old Boots (40% condition)
  Gold Ring (100% condition)

> browse
The Gilded Rose - Jeweler
Tier 2 | Merchant Guild
Merchant: Helena the Jeweler

> sell gold ring
You sell 1x Gold Ring for 500 crowns.
New gold total: 2750 crowns

> sell damaged iron sword
The Gilded Rose doesn't buy Damaged Iron Sword.

[Go to weaponsmith instead]

> sell damaged iron sword
You sell 1x Damaged Iron Sword for 45 crowns.
New gold total: 2795 crowns
```

### Scenario 4: Managing Your Shop
```
> shopmanage
Shop Management: The Witcher's Cache
Type: General Store
Tier: 2
Faction: Witcher Guild
Status: Open

Financials:
Gold Reserves: 1500 crowns
Markup: 150% (sell price)
Buyback: 50% (buy price)

Inventory:
Unique items: 8
Total items: 23

Recent Transactions:
📤 Swallow Potion x1 for 300 crowns
📥 Damaged Sword x1 for 50 crowns

> shopmanage prices 140 60
Updated prices for The Witcher's Cache:
Markup: 140% | Buyback: 60%

[More generous prices attract more customers]

> shopmanage restock
Restocked The Witcher's Cache!
Added 12 items across 7 different types.
```

## Tips and Best Practices

### For Players

1. **Always browse before buying** - compare prices
2. **Haggle for expensive purchases** - save significant gold
3. **Repair before selling** - get better prices
4. **Sell to appropriate shops** - get better buyback
5. **Check multiple shops** - find best prices
6. **Use social stats** - Cunning helps with merchants

### For Shop Owners

1. **Maintain gold reserves** - can't buy without gold
2. **Balanced pricing** - too high = no customers
3. **Regular restocking** - keep inventory fresh
4. **Faction alignment** - match your customer base
5. **Strategic location** - high-traffic areas
6. **Quality merchant NPC** - higher social stats resist haggling

### For GMs

1. **Vary shop tiers by location** - villages get tier 1-2, cities get 3-4
2. **Create faction-appropriate shops** - thematic consistency
3. **Set up restock rules** - automated inventory management
4. **Balance economy** - monitor transaction logs
5. **Reward shop ownership** - viable endgame goal
6. **Use social combat** - makes merchants interesting NPCs

## Technical Notes

### Database Models

- **Shop**: Main shop entity
- **ShopInventory**: Items currently in stock
- **ShopTransaction**: Transaction history
- **ShopRestockRule**: Defines what can be stocked

### Automatic Systems

- Restocking runs based on `restock_interval_hours`
- Social combat discounts stored in `character.ndb.shop_discount`
- Transaction logging is automatic
- Condition affects sell prices automatically

### Admin Interface

All shop models have Django admin interfaces for:
- Creating/editing shops
- Managing inventory
- Viewing transactions
- Setting up restock rules

Access via the admin panel at `/admin/`
