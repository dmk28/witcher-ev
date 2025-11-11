# Character Advancement System Guide

## Overview

The advancement system allows players to spend XP to improve their character's stats and skills. High-level advancements (levels 6-7) require GM approval to ensure exceptional abilities are narratively justified.

**XP Cost Formula:**

**Stats (Attributes):**
- Levels 1-5: New Rating × 10 XP
- Levels 6-7: New Rating × 20 XP (GM approval required)

**Skills:**
- Levels 1-5: New Rating × 5 XP
- Levels 6-7: New Rating × 15 XP (GM approval required)

## XP Cost Examples

### Stats
| Current | Target | Cost | Approval Required |
|---------|--------|------|-------------------|
| 3 | 4 | 40 XP | No |
| 4 | 5 | 50 XP | No |
| 5 | 6 | 120 XP | **Yes** |
| 6 | 7 | 140 XP | **Yes** |

### Skills
| Current | Target | Cost | Approval Required |
|---------|--------|------|-------------------|
| 2 | 3 | 15 XP | No |
| 4 | 5 | 25 XP | No |
| 5 | 6 | 90 XP | **Yes** |
| 6 | 7 | 105 XP | **Yes** |

## Player Commands

### Viewing Advancement Options

```
advance
```

Shows all possible advancements with:
- Current values
- Target values
- XP costs
- Affordability indicators (✓/✗)
- GM approval requirements (marked with *)

**Example Output:**
```
=======================================================================
Character Advancement Options
Available XP: 250
=======================================================================

Stats: (1-5: NR×10 XP | 6-7: NR×20 XP + GM approval)
  ✓ Strength        3 → 4   40 XP
  ✓ Agility         4 → 5   50 XP
  ✗ Intelligence    4 → 5   50 XP
  ✓ Reflexes        5 → 6   120 XP *

Skills: (1-5: NR×5 XP | 6-7: NR×15 XP + GM approval)
  ✓ Blades          4 → 5   25 XP
  ✓ Alchemy         3 → 4   20 XP
  ✗ Magery          5 → 6   90 XP *

* = Requires GM approval
```

### Advancing (Levels 1-5)

```
advance <stat/skill>
advance strength
advance blades
```

Immediately spends XP and increases the stat/skill by 1 level.

**Requirements:**
- Sufficient XP
- Target level ≤ 5
- Not already at maximum (stats: 7, skills: 10)

**Example:**
```
> advance strength
Advancement successful!
Strength 3 → 4
XP spent: 40
Remaining XP: 210
```

### Requesting Approval (Levels 6-7)

```
request <stat/skill> <justification>
request strength My character has been training with legendary warriors for months
request blades Defeated master swordsmen in multiple duels
```

Submits a request to GMs for high-level advancement.

**Requirements:**
- Sufficient XP (will be spent upon approval)
- Target level is 6 or 7
- No pending request for the same stat/skill
- Meaningful justification explaining narrative basis

**Example:**
```
> request blades Defeated the Champion of Cintra in a duel, trained with Witcher instructors
Request submitted!
Blades: 5 → 6
Cost: 90 XP
Request ID: 12

A GM will review your request.
```

### Viewing Advancement History

```
history
history <character>  (GM only)
```

Shows all past stat and skill improvements with dates, costs, and approvals.

**Example Output:**
```
=======================================================================
Advancement History: Geralt
=======================================================================
2025-11-11 | Stat: Strength 3 → 4 (-40 XP)
2025-11-10 | Skill: Blades 4 → 5 (-25 XP)
2025-11-09 | Skill: Alchemy 3 → 4 (-20 XP)
2025-11-08 | Stat: Reflexes 5 → 6 (-120 XP) (GM: Vesemir)

Current XP: 210
```

## GM Commands

### Viewing Pending Requests

```
approve
approvals
```

Shows all pending GM approval requests with details.

**Example Output:**
```
=======================================================================
Pending Advancement Approval Requests
=======================================================================

Request ID: 12
Character: Geralt
Advancement: blades 5 → 6
XP Cost: 90
Type: Skill Increase
Submitted: 2025-11-11 14:30
Justification: Defeated the Champion of Cintra in a duel, trained
with Witcher instructors for two months. Character arc focused on
becoming master swordsman.

Request ID: 13
Character: Yennefer
Advancement: intelligence 5 → 6
XP Cost: 120
Type: Stat Increase
Submitted: 2025-11-11 15:00
Justification: Studied ancient texts at Aretuza, solved magical
theorem that stumped senior mages.

Commands:
approve <id> [notes] - Approve request
deny <id> <reason> - Deny request
```

### Approving Requests

```
approve <request_id> [notes]
approve 12
approve 12 Excellent roleplay and in-character progression
```

Approves the request, immediately:
- Increases the character's stat/skill
- Deducts the XP cost
- Logs the advancement
- Notifies the player

**Example:**
```
> approve 12 Great roleplay and character development
Request approved!
Character: Geralt
Advancement: blades 5 → 6
XP deducted: 90

[Player receives notification:]
=== Advancement Approved ===
Your request for blades 5 → 6 has been approved by Vesemir!
XP spent: 90
Great roleplay and character development
```

### Denying Requests

```
deny <request_id> <reason>
deny 13 Need more in-game training and storyline development first
```

Denies the request and notifies the player with the reason.

**Example:**
```
> deny 13 Character needs more study time and in-game justification
Request denied.
Character: Yennefer
Advancement: intelligence 5 → 6

[Player receives notification:]
=== Advancement Request Denied ===
Your request for intelligence 5 → 6 was denied by Vesemir.
Reason: Character needs more study time and in-game justification
```

## Design Philosophy

### Why Approval for 6-7?

Levels 6-7 represent exceptional, near-legendary ability:

**Stats at 6-7:**
- **Strength 7**: Superhuman strength (Letho, enhanced Witchers)
- **Intelligence 7**: Genius-level intellect (Yennefer, Vilgefortz)
- **Reflexes 7**: Legendary speed (Ciri with Elder Blood)

**Skills at 6-7:**
- **Blades 6**: Master swordsman (Geralt, Cahir)
- **Blades 7**: Legendary fighter (Leo Bonhart)
- **Magery 7**: Archmage level (Yennefer, Philippa)

These levels should be:
- **Narratively earned** - significant in-game achievement
- **Rarely achieved** - most characters peak at 4-5
- **Story-significant** - character arc milestone

### Good vs. Bad Justifications

**Good Justifications:**
- ✓ "Trained intensively with Master Swordsmith for 3 months of roleplay"
- ✓ "Defeated legendary duelist NPC in climactic storyline battle"
- ✓ "Studied ancient texts, solved magical puzzle in recent quest"
- ✓ "Character arc focused on becoming strongest warrior, achieved victory in tournament"

**Bad Justifications:**
- ✗ "I want to be stronger"
- ✗ "Everyone else is high level"
- ✗ "I have the XP"
- ✗ "Just because"

GMs should require:
1. **In-game events** supporting the advancement
2. **Roleplay investment** in the area being advanced
3. **Story significance** - advancement marks meaningful progress
4. **Balance consideration** - not creating overpowered characters

## Advancement Strategy Tips

### For Players

**Early Game (XP 0-500):**
- Focus on core stats (3-4) and primary skills (3-4)
- Broad foundation better than one maxed skill
- Example: Witcher with Strength 4, Agility 4, Blades 4, Sign Sorcery 3

**Mid Game (XP 500-1500):**
- Specialize in role-defining areas
- Push primary stat/skill to 5
- Develop supporting skills (3-4)
- Example: Combat specialist with Blades 5, Athletics 4, Resistance 4

**Late Game (XP 1500+):**
- Consider legendary advancements (6-7)
- Ensure narrative justification for GM approval
- Round out character with remaining points
- Example: Master swordsman with Blades 6, Strength 5, Reflexes 5

**XP Efficiency:**
- Low levels cheap: Skill 1→2 = 10 XP, 2→3 = 15 XP (25 total)
- High levels expensive: Skill 5→6 = 90 XP, 6→7 = 105 XP (195 total!)
- Better to have multiple 4s than one 6

### For GMs

**Approval Guidelines:**

**Automatic Approve:**
- Strong narrative justification
- Significant roleplay investment
- Recent in-game accomplishment
- Fits character arc
- Doesn't break game balance

**Need More Info:**
- Justification vague
- No recent relevant roleplay
- Request for clarification acceptable

**Should Deny:**
- No narrative justification
- Character hasn't engaged with that area
- Would break game balance
- Player gaming the system

**Approval Rate:**
- Aim for ~70-80% approval rate
- Shows players that preparation matters
- Encourages meaningful roleplay
- Maintains legendary status of 6-7

## Advanced Features

### Tracking Character Growth

Every advancement is logged with:
- Date and time
- Old and new values
- XP cost
- GM approval (if required)
- Approving GM name

This creates a complete record of character progression for:
- Story purposes (character biography)
- Balance auditing (ensure fair advancement)
- Player achievement tracking
- Narrative callbacks (remember that training arc?)

### Admin Interface

GMs can use Django admin (/admin/) to:

**AdvancementLog:**
- View all character advancements
- Filter by type, approval requirement, date
- Search by character or stat/skill name
- Audit XP spending patterns

**ApprovalRequest:**
- View/manage all approval requests
- Filter by status (pending/approved/denied)
- Search by character
- Review justifications and GM notes
- Manual approval/denial if needed

### Integration with Other Systems

**XP Sources:**
- Mission completion rewards
- Combat encounter victories
- Crafting achievements
- Social combat victories
- GM-awarded story XP

**Character Sheet:**
- Use `sheet` or `stat` commands to view current stats/skills
- Use `advance` to see advancement costs
- XP total displayed on character sheet

**Vocation Bonuses:**
- Base stats include vocation modifiers
- Advancement increases **base** stat, not total
- Total = Base + Vocation + Country bonuses

## Example Progression Path

### Geralt - Witcher Build

**Starting (Chargen):**
- Stats: All base 1, +vocational bonuses
- Skills: Sign Sorcery 2, Blades 3, Alchemy 2, Resistance 2
- XP: 0

**Early Career (500 XP spent):**
- Strength 1→3 (60 XP)
- Agility 1→3 (60 XP)
- Reflexes 1→4 (100 XP)
- Blades 3→5 (45 XP)
- Alchemy 2→4 (35 XP)
- Sign Sorcery 2→4 (35 XP)
- Resistance 2→4 (35 XP)
- Athletics 0→3 (30 XP)
Total: 400 XP, 100 XP saved

**Mid Career (1500 XP total spent):**
- Strength 3→4 (40 XP)
- Agility 3→4 (40 XP)
- Reflexes 4→5 (50 XP)
- Perception 1→3 (60 XP)
- Blades 5→6 (90 XP, **GM approved**: "Legendary monster hunter")
- Alchemy 4→5 (25 XP)
- Crossbows 0→3 (30 XP)
Additional: 335 XP

**Legendary Status (2500+ XP):**
- Strength 4→5 (50 XP)
- Agility 4→5 (50 XP)
- Reflexes 5→6 (120 XP, **GM approved**: "White Wolf legacy")
- Blades 6→7 (105 XP, **GM approved**: "Defeated Vilgefortz")
- Sign Sorcery 4→5 (25 XP)
Additional: 350 XP

Total spent on legendary advancements: 315 XP for +3 levels (6→7 twice, 5→6 once)

## Common Questions

**Q: Can I save XP for later?**
A: Yes! XP never expires. Save up for expensive advancements.

**Q: What if my approval request is denied?**
A: Work on building narrative justification through roleplay, then resubmit later.

**Q: Can I lower a stat/skill to regain XP?**
A: No. Advancements are permanent.

**Q: Do vocation bonuses count toward the 6-7 cap?**
A: No. Vocation bonuses are separate. Base stat can be 7 + vocation bonus.

**Q: How much XP should I earn per session?**
A: GM discretion, typically 10-50 XP per session depending on accomplishments.

**Q: Can I advance stats/skills above 7/10?**
A: No. 7 is maximum for stats, 10 for skills (though skills 8-10 also require GM approval).

**Q: What if GM is unavailable for my 6-7 approval?**
A: Request stays pending until reviewed. No time limit.

**Q: Can I withdraw an approval request?**
A: Contact a GM to mark it as denied with "withdrawn" note.

## Balance Considerations

### Stat Scaling

Stats scale significantly in effectiveness:

- **1-3**: Below average to average
- **4-5**: Above average to exceptional
- **6**: Masterful, near-legendary
- **7**: Legendary, peak human/enhanced

Going from 5→6 costs 120 XP for stats because it represents a massive power increase.

### Skill Scaling

Skills are more granular:

- **0-2**: Untrained to novice
- **3-4**: Competent to skilled
- **5**: Expert level
- **6-7**: Master to legendary master
- **8-10**: Superhuman mastery (very rare)

The 5→6 jump (90 XP) represents crossing from "very good" to "one of the best in the world."

### Campaign Longevity

Advancement costs are balanced for:
- **Short campaigns (5-10 sessions)**: Characters reach 4-5 in key areas
- **Medium campaigns (20-40 sessions)**: Characters might reach 6 in 1-2 areas
- **Long campaigns (50+ sessions)**: Characters become legendary (multiple 6-7s)

This pacing ensures:
- Meaningful progression throughout campaign
- Legendary status feels earned
- Players don't "max out" too quickly
- GM approval system maintains narrative weight

## Technical Notes

### Database Models

**AdvancementLog:**
- Records every stat/skill increase
- Tracks XP costs and GM approvals
- Permanent history (never deleted)

**ApprovalRequest:**
- Pending/approved/denied requests
- Stores justifications and GM notes
- Reviewed by GM with timestamp

### Validators

- Stats capped at 7
- Skills capped at 10
- XP costs calculated automatically
- Approval requirements enforced

### Commands

All advancement commands integrated into default character command set:
- `advance` - View/spend XP
- `request` - Submit approval requests
- `approve`/`deny` - GM tools (staff-locked)
- `history` - View advancement log
