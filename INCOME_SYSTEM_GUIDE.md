# Organization and Income System Guide

This document explains the passive income system for the Witcher RPG MUD.

## Table of Contents
- [Overview](#overview)
- [Organization Types](#organization-types)
- [Income Mechanics](#income-mechanics)
- [Player Commands](#player-commands)
- [GM Commands](#gm-commands)
- [Examples](#examples)

---

## Overview

The income system provides passive monthly income to characters based on their organizational affiliations and ranks. Characters can join multiple organizations and collect income from each one monthly.

### Key Features
- **Rank-Based Income**: Higher ranks provide more income
- **Organization Multipliers**: Prestigious organizations pay more
- **Tithing System**: Members can pay a percentage to organization treasury
- **Leadership Benefits**: Leaders receive a share of tithing
- **Trading Companies**: Investment-based returns
- **30-Day Cooldown**: Prevent income farming

---

## Organization Types

### 1. Noble House
Aristocratic families and noble estates.

**Example:** House Foltest, House Henselt, House Stennis

**Typical Setup:**
- Base Income Multiplier: 1.0 - 2.0 (prestigious houses)
- Member Tithing: 0-10%
- Requires Approval: Yes

**Example Incomes:**
- Rank 1 Guard: 100 crowns/month
- Rank 2 Knight: 300 crowns/month
- Rank 3 Baron: 800 crowns/month
- Rank 4 Count: 2,000 crowns/month
- Rank 5 Duke: 5,000 crowns/month

### 2. Witcher School
Professional monster hunters.

**Example:** School of the Wolf, School of the Cat, School of the Bear

**Typical Setup:**
- Base Income Multiplier: 1.0
- Member Tithing: 10-20% (supports the school)
- Leader Share: 50-80%
- Requires Approval: Yes

**Example:**
- Rank 1 Apprentice: 100 crowns/month, pays 10 crowns tithing
- Rank 2 Witcher (Fort Leader): Receives tithing from 10 witchers = 100 crowns/month
- Total leader income: 500-2,000 crowns/month depending on membership

### 3. Trading Company
Merchant guilds and trading consortiums.

**Example:** Vivaldi Bank, Merchant's Guild

**Typical Setup:**
- Base Income Multiplier: 1.0 - 1.5
- Member Tithing: 0%
- Investment System: Yes (5% monthly return)
- Requires Approval: No (open membership)

**Investment Example:**
- Invest 10,000 crowns
- Receive 500 crowns/month (5% return)
- Rank income + investment returns

### 4. Military Order
Organized military forces.

**Example:** Order of the Flaming Rose, Temerian Special Forces

**Typical Setup:**
- Base Income Multiplier: 1.0 - 1.5
- Member Tithing: 5-10%
- Requires Approval: Yes

### 5. Magical Academy
Schools of magic and sorcery.

**Example:** Aretuza, Ban Ard Academy

**Typical Setup:**
- Base Income Multiplier: 1.5 - 2.0
- Member Tithing: 0-5%
- Requires Approval: Yes

### 6. Criminal Syndicate
Underground organizations.

**Example:** Thieves' Guild, Assassin's Guild

**Typical Setup:**
- Base Income Multiplier: 0.8 - 1.2
- Member Tithing: 20-30% (protection money)
- Leader Share: 60-80%
- Requires Approval: Yes

### 7. Professional Guild
Craftsmen and artisan organizations.

**Example:** Blacksmiths' Guild, Alchemists' Guild

**Typical Setup:**
- Base Income Multiplier: 1.0
- Member Tithing: 5-10% (guild dues)
- Requires Approval: No

### 8. Religious Order
Churches and religious organizations.

**Example:** Church of the Eternal Fire, Melitele's Temple

**Typical Setup:**
- Base Income Multiplier: 0.8 - 1.5
- Member Tithing: 10-20% (tithes)
- Requires Approval: Yes

---

## Income Mechanics

### Base Income by Rank

| Rank | Monthly Income | Description |
|------|----------------|-------------|
| 1    | 100 crowns     | Entry level |
| 2    | 300 crowns     | Experienced |
| 3    | 800 crowns     | Senior      |
| 4    | 2,000 crowns   | Elite       |
| 5    | 5,000 crowns   | Leadership  |

### Organization Multiplier

The base income is modified by the organization's `base_income_multiplier`:

```
Actual Income = Base Income × Multiplier
```

**Example:**
- Rank 3 member in a prestigious house (2.0x multiplier)
- Base: 800 crowns × 2.0 = 1,600 crowns/month

### Tithing System

Organizations can require members to pay a percentage to the treasury:

```
Tithe = Base Income × (Tithe Percentage / 100)
Net Income = Base Income - Tithe
```

**Example:**
- Rank 2 Witcher: 300 crowns base
- 10% tithing = 30 crowns to treasury
- Member receives: 270 crowns
- Leader receives: 50% of 30 = 15 crowns (if leader share is 50%)

### Leadership Income

Leaders receive a share of all tithing:

```
Leader Income = (Total Tithing from All Members) × (Leader Share Percentage / 100)
```

**Example - Witcher Fort:**
- 10 Rank 1 Witchers paying 10% tithing: 10 × 10 = 100 crowns total
- 5 Rank 2 Witchers paying 10% tithing: 5 × 30 = 150 crowns total
- Total tithing: 250 crowns
- Leader share (80%): 200 crowns/month

### Trading Company Investments

Members can invest gold for passive returns:

```
Monthly Return = Personal Investment × 0.05 (5%)
```

**Example:**
- Invest 50,000 crowns
- Receive 2,500 crowns/month
- Plus base rank income

### Collection Cooldown

Income can be collected once every 30 days per organization.

---

## Player Commands

### View Available Organizations

```
+organizations
+organizations <name>
+organizations/type <type>
+organizations/all
```

**Examples:**
```
+organizations
+organizations House Foltest
+organizations/type noble_house
+organizations/all
```

### Join an Organization

```
+orgjoin <organization name>
```

Submits a membership request. Some organizations require approval.

**Example:**
```
+orgjoin House Foltest
```

### Leave an Organization

```
+orgleave <organization name>
```

Deactivates your membership.

**Example:**
```
+orgleave House Foltest
```

### Collect Income

```
+income
```

Collects monthly income from all active memberships.

**Output Example:**
```
======================================================================
Monthly Income Collection
======================================================================
✓ House Foltest
  Rank: 2
  Role: Knight
  Income: 600 crowns

✓ Merchants Guild
  Rank: 1
  Investment Returns: 500 crowns
  Income: 600 crowns

----------------------------------------------------------------------
Total Collected: 1,200 crowns
New Balance: 15,450 crowns
======================================================================
```

### Invest in Trading Company

```
+orginvest <organization name> = <amount>
```

Invest gold in a trading company for passive returns.

**Example:**
```
+orginvest Vivaldi Bank = 10000
```

### Manage Your Organization (Leaders Only)

```
+orgmanage <organization>
+orgmanage <organization>/promote <member> = <rank>
+orgmanage <organization>/demote <member> = <rank>
+orgmanage <organization>/setrole <member> = <role>
+orgmanage <organization>/approve <member>
+orgmanage <organization>/kick <member>
+orgmanage <organization>/transfer <member>
```

**Examples:**
```
+orgmanage House Foltest
+orgmanage House Foltest/promote Geralt = 3
+orgmanage House Foltest/setrole Geralt = Royal Guard Captain
+orgmanage House Foltest/approve Ciri
```

---

## GM Commands

### Create Organization

```
+orgcreate <name> = <type>
```

**Organization Types:**
- `noble_house`
- `witcher_school`
- `trading_company`
- `military_order`
- `magical_academy`
- `criminal_syndicate`
- `guild`
- `religious_order`

**Example:**
```
+orgcreate House Foltest = noble_house
+orgcreate School of the Wolf = witcher_school
+orgcreate Vivaldi Bank = trading_company
```

### Edit Organization

```
+orgedit <organization>/desc = <description>
+orgedit <organization>/leader = <character>
+orgedit <organization>/multiplier = <number>
+orgedit <organization>/tithe = <percentage>
+orgedit <organization>/leadershare = <percentage>
+orgedit <organization>/approval = <yes|no>
+orgedit <organization>/active = <yes|no>
+orgedit <organization>/investment = <level>
```

**Examples:**
```
+orgedit House Foltest/desc = A prestigious noble house from Temeria, known for its military prowess.
+orgedit House Foltest/leader = KingFoltest
+orgedit House Foltest/multiplier = 2.0
+orgedit House Foltest/tithe = 10
+orgedit House Foltest/leadershare = 50
+orgedit House Foltest/approval = yes
```

---

## Examples

### Example 1: Noble House Guard

**Setup:**
```
+orgcreate House Foltest = noble_house
+orgedit House Foltest/desc = Royal house of Temeria
+orgedit House Foltest/multiplier = 1.5
+orgedit House Foltest/tithe = 0
+orgedit House Foltest/leader = KingFoltest
```

**Player joins:**
```
+orgjoin House Foltest
```

**GM approves:**
```
+orgmanage House Foltest/approve PlayerName
```

**Player collects:**
```
+income
> Rank 1 Guard: 150 crowns/month (100 × 1.5)
```

### Example 2: Witcher School with Tithing

**Setup:**
```
+orgcreate School of the Wolf = witcher_school
+orgedit School of the Wolf/desc = Elite monster hunters from Kaer Morhen
+orgedit School of the Wolf/multiplier = 1.0
+orgedit School of the Wolf/tithe = 10
+orgedit School of the Wolf/leadershare = 80
+orgedit School of the Wolf/leader = Vesemir
```

**10 witchers join at Rank 1:**
- Each witcher: 100 crowns base - 10 crowns tithe = 90 crowns/month
- Total tithing: 100 crowns
- Leader Vesemir: 80 crowns/month from tithing

**5 witchers promoted to Rank 2:**
- Each witcher: 300 crowns base - 30 crowns tithe = 270 crowns/month
- Total new tithing: 5 × 30 = 150 crowns
- Leader Vesemir now gets: (5 × 10 + 5 × 30) × 0.8 = 160 crowns/month

### Example 3: Trading Company with Investments

**Setup:**
```
+orgcreate Vivaldi Bank = trading_company
+orgedit Vivaldi Bank/desc = Premier banking institution
+orgedit Vivaldi Bank/multiplier = 1.0
+orgedit Vivaldi Bank/tithe = 0
+orgedit Vivaldi Bank/investment = 10
+orgedit Vivaldi Bank/approval = no
```

**Player joins and invests:**
```
+orgjoin Vivaldi Bank
+orginvest Vivaldi Bank = 20000
```

**Player income:**
```
+income
> Rank 1 Banker: 100 crowns (base)
> Investment Returns: 1,000 crowns (5% of 20,000)
> Total: 1,100 crowns/month
```

### Example 4: Criminal Syndicate

**Setup:**
```
+orgcreate Thieves Guild = criminal_syndicate
+orgedit Thieves Guild/desc = Underground network of thieves
+orgedit Thieves Guild/multiplier = 1.0
+orgedit Thieves Guild/tithe = 25
+orgedit Thieves Guild/leadershare = 70
+orgedit Thieves Guild/leader = ShadowMaster
+orgedit Thieves Guild/approval = yes
```

**20 thieves at Rank 1:**
- Each thief: 100 crowns - 25 crowns tithe = 75 crowns/month
- Total tithing: 500 crowns
- Guild Master: 350 crowns/month (70% of 500)

---

## Economic Impact

### For Players

**Low-Level Character (Rank 1):**
- One organization: 100-200 crowns/month
- Two organizations: 200-400 crowns/month
- With investment (10,000 crowns): +500 crowns/month

**Mid-Level Character (Rank 2-3):**
- One organization: 300-1,200 crowns/month
- Two organizations: 600-2,400 crowns/month
- With investment (50,000 crowns): +2,500 crowns/month

**High-Level Character (Rank 4-5):**
- One organization: 2,000-10,000 crowns/month
- Leader of multiple organizations: 5,000-20,000+ crowns/month

### For Leaders

**Small Organization (10 members):**
- With 10% tithing on Rank 1 members: 100 crowns/month
- With 50% leader share: 50 crowns/month

**Large Organization (50 members):**
- Mix of ranks with 10% average tithing: 1,500 crowns/month
- With 50% leader share: 750 crowns/month

**Prestigious House (100+ members):**
- With diverse ranks and tithing: 10,000+ crowns/month possible

---

## Admin Interface

Organizations can be managed through the Django admin:

`http://your-server/admin/witcher_rpg/organization/`

Features:
- Inline member management
- Income calculations display
- Approval workflow
- Audit logs

---

## Database Models

### Organization
- **name**: Unique organization name
- **organization_type**: One of 8 types
- **leader**: Foreign key to character
- **treasury**: Organization gold
- **investment_level**: For trading companies
- **base_income_multiplier**: Income modifier (default 1.0)
- **member_tithe_percentage**: 0-100
- **leader_share_percentage**: 0-100
- **requires_approval**: Boolean
- **is_active**: Boolean

### OrganizationMembership
- **organization**: Foreign key
- **member**: Foreign key to character
- **organization_rank**: 1-5
- **role**: Custom title
- **personal_investment**: For trading companies
- **is_active**: Boolean
- **is_approved**: Boolean
- **last_income_collection**: Timestamp

### IncomeLog
- **character**: Foreign key
- **organization**: Foreign key (nullable)
- **amount**: Gold collected
- **source**: Description
- **timestamp**: Auto-generated

---

## Future Enhancements

### Planned Features
1. **Organization Events**: Special missions for members
2. **Reputation System**: Faction standing affects income
3. **Organization Upgrades**: Spend treasury to increase multipliers
4. **Territory Control**: Organizations can control regions
5. **Inter-Organization Conflicts**: Wars and alliances
6. **Seasonal Bonuses**: Temporary income boosts
7. **Bankruptcy System**: Organizations can run out of money
8. **Inheritance**: Transfer leadership on death/retirement

### Balance Considerations
- Monitor average player income vs. item costs
- Adjust rank requirements based on vocation
- Scale tithing percentages based on organization size
- Cap maximum income from single organization
- Implement diminishing returns on multiple memberships

---

## Technical Notes

### Files
- **Models**: `world/witcher_rpg/organization_models.py`
- **Commands**: `commands/income_commands.py`
- **Migration**: `world/witcher_rpg/migrations/0019_organization_income_system.py`
- **Admin**: `world/witcher_rpg/admin.py` (Organization admin section)

### Dependencies
- Django ORM
- Evennia ObjectDB
- WitcherCharacter model
- Timezone utilities

### Performance
- Income collection triggers database queries per membership
- Consider caching organization data for high-traffic servers
- Audit logs can grow large; implement rotation policy
