# Communication System Guide

Complete guide to the Witcher RPG communication system including paging and organization channels.

## Table of Contents
- [Overview](#overview)
- [Paging System](#paging-system)
- [Channel System](#channel-system)
- [Organization Channels](#organization-channels)
- [GM Commands](#gm-commands)
- [Examples](#examples)

---

## Overview

The communication system provides private messaging (paging) and public/private channels for in-game communication. Organization channels automatically manage subscriptions based on membership.

### Key Features
- **MUSH-style paging** with history tracking
- **Organization channels** that auto-subscribe/unsubscribe members
- **Faction channels** based on country or vocation
- **Private channels** with owner control
- **AFK/Busy status** for pages
- **Multi-target paging** for group messages

---

## Paging System

### Send a Page

```
+page <player> = <message>
page <player> = <message>
tell <player> = <message>
```

Send a private message to another player.

**Examples:**
```
+page Geralt = Hey, want to group up for that quest?
page Yennefer = Meeting at the tavern in 10 minutes
tell Ciri = Watch out, bandits to the north!
```

### Multi-Player Paging

```
+page <player1>,<player2>,<player3> = <message>
```

Send a page to multiple players at once.

**Example:**
```
+page Geralt,Yennefer,Triss = Party meeting in 5 minutes!
```

**Output (to sender):**
```
[Page to Geralt, Yennefer, Triss at 14:30] Party meeting in 5 minutes!
```

**Output (to each recipient):**
```
[Page from YourName at 14:30] Party meeting in 5 minutes!
```

### View Page History

```
+pagehistory [number]
+ph [number]
```

View your recent pages (sent and received). Default shows last 10, maximum 50.

**Example:**
```
+pagehistory 20
```

**Output:**
```
======================================================================
Page History (Last 20 messages)
======================================================================

[2025-11-11 14:25:30] From Geralt:
        Ready for that quest?

[2025-11-11 14:26:15] To Geralt:
        Yes, meet at the gate

[2025-11-11 14:30:00] From Yennefer:
        Don't forget the potions

======================================================================
```

### AFK Status

```
+afk [message]
+afk/clear
```

Set yourself as Away From Keyboard. Others paging you will see your AFK message.

**Examples:**
```
+afk Taking a break, back in 15 mins
+afk Dinner time!
+afk/clear
```

When someone pages you while AFK:
```
> +page PlayerName = Hi there
Yennefer is AFK: Taking a break, back in 15 mins
[Page to Yennefer at 14:35] Hi there
```

### Busy Status

```
+busy [message]
+busy/clear
```

Set yourself as Busy/Do Not Disturb. Similar to AFK but indicates you're actively doing something.

**Examples:**
```
+busy In combat, can't talk
+busy RPing, please don't disturb
+busy/clear
```

---

## Channel System

### View Available Channels

```
+channels
+channels/all
```

List all channels you can access. Use `/all` to see all channels in the game (including ones you don't have access to).

**Output:**
```
======================================================================
Your Channels
======================================================================

✓ Public (PublicChannel) - 15 subscribers
        Main public channel for all players

✓ House Foltest (OrganizationChannel) - 8 subscribers

✗ School of the Wolf (OrganizationChannel) - 5 subscribers

======================================================================
Use channel <name> = <message> to send to a channel.
Use addcom <alias> = <channel> to create a channel alias.
======================================================================
```

**Legend:**
- ✓ = You are subscribed
- ✗ = Not subscribed (but have access)

### Using Channels

Evennia's default channel commands work with all channels:

```
channel <name> = <message>
<alias> <message>
```

**Examples:**
```
channel Public = Hello everyone!
channel House Foltest = Meeting at the keep tonight

# With aliases (set using addcom)
pub Hello everyone!
hf Meeting at the keep tonight
```

### Channel Aliases

Create shortcuts for channels:

```
addcom <alias> = <channel name>
delcom <alias>
allcom
```

**Examples:**
```
addcom pub = Public
addcom hf = House Foltest
addcom wolf = School of the Wolf

# Now you can use:
pub Hello!
hf Anyone available?
wolf Heading to Kaer Morhen
```

---

## Organization Channels

Organization channels automatically manage membership based on your organization status.

### How It Works

1. **Joining an Organization**
   - When you join (or get approved): Automatically subscribed to org channel
   - Channel name matches organization name exactly

2. **Leaving an Organization**
   - When you leave or get kicked: Automatically unsubscribed from org channel
   - Lose access immediately

3. **Access Control**
   - Only active, approved members can access org channels
   - Leaders and GMs always have access
   - Pending members cannot access until approved

### Example Flow

**Join Organization:**
```
> +orgjoin House Foltest
You have joined House Foltest!
You will receive 200 crowns per month.
Use +income to collect your monthly stipend.
You have been added to the House Foltest channel.
```

**Use Channel:**
```
> addcom hf = House Foltest
> hf Greetings, fellow members of House Foltest!
[House Foltest] Geralt: Greetings, fellow members of House Foltest!
```

**Leave Organization:**
```
> +orgleave House Foltest
You have left House Foltest.
You have been removed from the House Foltest channel.
```

### Organization Channel Setup

When creating an organization, the GM should also create its channel:

```
+channelcreate <org name> = org:<org name>
```

**Example:**
```
+orgcreate House Foltest = noble_house
+channelcreate House Foltest = org:House Foltest
```

Now when players join House Foltest, they'll automatically be added to the channel!

---

## GM Commands

### Create a Channel

```
+channelcreate <name> = <type>
```

**Channel Types:**

**Public Channel:**
```
+channelcreate Public = public
+channelcreate OOC = public
+channelcreate Newbie = public
```

**Organization Channel:**
```
+channelcreate <org name> = org:<organization name>
```
Links to an existing organization. Auto-manages subscriptions.

**Examples:**
```
+channelcreate House Foltest = org:House Foltest
+channelcreate School of the Wolf = org:School of the Wolf
+channelcreate Vivaldi Bank = org:Vivaldi Bank
```

**Faction Channel:**
```
+channelcreate <name> = faction:<country or vocation>
```
Accessible to all players from that country or with that vocation.

**Examples:**
```
+channelcreate Temeria = faction:Temeria
+channelcreate Nilfgaard = faction:Nilfgaard
+channelcreate Witchers = faction:Witcher
+channelcreate Merchants = faction:Merchant
```

**Private Channel:**
```
+channelcreate <name> = private
```
Owner-controlled private channel.

**Example:**
```
+channelcreate StaffChat = private
```

### Delete a Channel

```
+channeldelete <name>
```

Permanently deletes a channel. Cannot be undone.

**Example:**
```
+channeldelete OldChannel
```

---

## Channel Types Detail

### PublicChannel
- Available to all players
- Anyone can join/leave
- Default for general communication

### OrganizationChannel
- Linked to a specific organization
- Access controlled by membership (active + approved)
- Auto-subscribes on join/approval
- Auto-unsubscribes on leave/kick
- Builders always have access

**Access Logic:**
```
- Must be active member (is_active=True)
- Must be approved (is_approved=True)
- OR be a Builder/GM
```

### FactionChannel
- Country-based: All players from that country
- Vocation-based: All players with that vocation
- Rank-based: Players above certain social rank
- Good for IC regional/professional communication

### PrivateChannel
- Owner controls access
- Owner can add/remove members
- Useful for small groups, staff channels, etc.

---

## Examples

### Example 1: Noble House Setup

**GM creates organization and channel:**
```
+orgcreate House Foltest = noble_house
+orgedit House Foltest/desc = The royal house of Temeria, known for military strength.
+orgedit House Foltest/multiplier = 1.5
+channelcreate House Foltest = org:House Foltest
```

**Player joins:**
```
> +orgjoin House Foltest
Membership request submitted to House Foltest.
Your request requires approval from the organization's leadership.
```

**Leader approves:**
```
> +orgmanage House Foltest/approve Geralt
Geralt's membership in House Foltest has been approved.
```

**Geralt automatically gets:**
- Active membership
- Monthly income eligibility
- Auto-subscribed to "House Foltest" channel

**Geralt can now:**
```
> addcom hf = House Foltest
> hf My lords, I am at your service!
[House Foltest] Geralt: My lords, I am at your service!
```

### Example 2: Witcher School Communication

**GM setup:**
```
+orgcreate School of the Wolf = witcher_school
+orgedit School of the Wolf/tithe = 10
+orgedit School of the Wolf/leadershare = 80
+channelcreate School of the Wolf = org:School of the Wolf
```

**Witchers join and communicate:**
```
> +orgjoin School of the Wolf
You have joined School of the Wolf!
You have been added to the School of the Wolf channel.

> addcom wolf = School of the Wolf
> wolf Brothers, there's a contract in Novigrad
[School of the Wolf] Geralt: Brothers, there's a contract in Novigrad
[School of the Wolf] Eskel: I'll check it out
[School of the Wolf] Lambert: Count me in
```

### Example 3: Country-Wide Channels

**GM creates faction channels:**
```
+channelcreate Temeria = faction:Temeria
+channelcreate Nilfgaard = faction:Nilfgaard
```

**All Temerians automatically have access:**
```
> +channels
...
✓ Temeria (FactionChannel) - 25 subscribers
        Channel for all citizens of Temeria
...

> addcom tem = Temeria
> tem Long live King Foltest!
[Temeria] Guard: Long live King Foltest!
```

### Example 4: Private Group Channel

**Player creates private channel (GM only):**
```
+channelcreate AdventureParty = private
```

**GM or owner manages access via Evennia's built-in channel commands:**
```
ccreate AdventureParty
cset AdventureParty/desc = Private channel for our adventuring group
# Add members manually or they can request access
```

### Example 5: Multi-Organization Member

**Player in multiple orgs:**
```
> +organizations
...
✓ House Foltest
✓ Merchants Guild
...

> +channels
...
✓ House Foltest (OrganizationChannel) - 8 subscribers
✓ Merchants Guild (OrganizationChannel) - 15 subscribers
✓ Temeria (FactionChannel) - 25 subscribers
...

> addcom hf = House Foltest
> addcom mg = Merchants Guild
> addcom tem = Temeria

# Can participate in all channels
> hf Noble business here
> mg Anyone selling iron ore?
> tem Temeria stands strong!
```

---

## Integration with Game Systems

### Organization System Integration

The channel system is tightly integrated with organizations:

**Automatic Subscription Points:**
1. `+orgjoin` (no approval required)
2. `+orgmanage <org>/approve <player>` (GM approval)

**Automatic Unsubscription Points:**
1. `+orgleave <org>`
2. `+orgmanage <org>/kick <player>`

**Access Verification:**
- Checked on every channel message
- Based on OrganizationMembership status
- Real-time (if kicked, immediately lose access)

### Character System Integration

Faction channels check:
- **Character.country** for country-based channels
- **Character.vocation.name** for vocation-based channels
- **Character.social_rank** for rank-based channels

---

## Best Practices

### For Players

1. **Set up aliases** for channels you use frequently
   ```
   addcom pub = Public
   addcom hf = House Foltest
   ```

2. **Use AFK/Busy** when unavailable
   ```
   +afk Taking a break
   +busy In important RP scene
   ```

3. **Check page history** to catch up on missed messages
   ```
   +ph 30
   ```

4. **Use appropriate channels** for topics
   - Org channels: Organization business
   - Faction channels: Regional/professional matters
   - Public: General discussion
   - Pages: Private conversations

### For GMs

1. **Create org channels** when creating organizations
   ```
   +orgcreate <name> = <type>
   +channelcreate <name> = org:<name>
   ```

2. **Create faction channels** for major regions
   ```
   +channelcreate Temeria = faction:Temeria
   +channelcreate Nilfgaard = faction:Nilfgaard
   +channelcreate Redania = faction:Redania
   ```

3. **Create vocation channels** for professional groups
   ```
   +channelcreate Witchers = faction:Witcher
   +channelcreate Merchants = faction:Merchant
   +channelcreate Soldiers = faction:Soldier
   ```

4. **Monitor channels** for IC/OOC separation
   - Org channels should be IC
   - Public can be OOC or IC depending on policy
   - Consider separate IC/OOC public channels

---

## Technical Details

### Channel Access Logic

**OrganizationChannel:**
```python
def access(accessing_obj):
    # Builders always access
    if accessing_obj.is_builder:
        return True

    # Check active, approved membership
    membership = OrganizationMembership.objects.get(
        organization=self.organization,
        member=accessing_obj,
        is_active=True,
        is_approved=True
    )
    return membership.exists()
```

**FactionChannel:**
```python
def access(accessing_obj):
    character = WitcherCharacter.objects.get(db_object=accessing_obj)

    if faction_type == 'country':
        return character.country == faction_value
    elif faction_type == 'vocation':
        return character.vocation.name == faction_value
    elif faction_type == 'social_rank':
        return character.social_rank >= faction_value
```

### Page Storage

Pages are stored in character attributes:
- `character.db.page_history` - List of page dictionaries
- Maximum 50 messages stored
- Includes timestamp, direction, sender/recipient, message

**Page Dictionary Structure:**
```python
{
    'from': 'SenderName',  # or 'to' for sent pages
    'message': 'The message text',
    'timestamp': datetime_object,
    'direction': 'received'  # or 'sent'
}
```

---

## Troubleshooting

### "You don't have access to that channel"
- **Org Channel:** Check you're an active, approved member
- **Faction Channel:** Check your character's country/vocation matches
- **Private Channel:** Request access from the owner

### "Channel not found"
- Check spelling with `+channels`
- GM may need to create it: `+channelcreate`

### Not receiving org channel messages
- Verify membership: `+organizations <name>`
- Check subscription: `+channels` (should show ✓)
- May need re-approval if kicked/rejoined

### Page not delivering
- Target may be offline
- Check name spelling
- Target may have page filtering (future feature)

---

## Future Enhancements

Planned features:
- Channel moderation (mute, ban)
- Page filtering/blocking
- Channel descriptions and MOTDs
- Channel history/logs
- Cross-game IRC/Discord bridges
- Channel emotes/poses
- @emit to channels
- Channel permissions (operator, voice, etc.)

---

## Commands Summary

### Player Commands

**Paging:**
- `+page <player> = <message>` - Send page
- `+pagehistory [n]` - View page history
- `+afk [message]` - Set AFK status
- `+busy [message]` - Set busy status

**Channels:**
- `+channels` - List accessible channels
- `channel <name> = <message>` - Send to channel
- `addcom <alias> = <channel>` - Create alias
- `delcom <alias>` - Remove alias
- `allcom` - List aliases

### GM Commands

- `+channelcreate <name> = <type>` - Create channel
- `+channeldelete <name>` - Delete channel
- Organization channel auto-creation recommended
- Use existing Evennia channel admin for advanced management

---

## Files

**Channel Types:** `typeclasses/channels.py`
**Commands:** `commands/comms_commands.py`
**Integration:** `commands/income_commands.py` (org join/leave hooks)
**Registration:** `commands/default_cmdsets.py`
