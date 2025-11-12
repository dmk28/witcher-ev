# Launch and Testing Guide
## Witcher: The Northern Kingdoms

This guide covers everything needed to launch the server and test all game systems.

---

## Prerequisites Checklist

✅ **Completed**:
- All migrations applied (21 migrations)
- 40 weapons, armor, and shields populated
- Communication system implemented
- MUSH formatting system active
- Professional front page created
- All game systems coded and ready

⚠️ **Before First Launch**:
- Create superuser account (GM/Admin)
- Configure server settings if needed
- Test all systems systematically

---

## Part 1: Initial Server Setup

### Step 1: Create Superuser Account

The server needs a superuser (Account #1) before it can run properly. This will be the primary GM account.

```bash
# Create the superuser
export DJANGO_SETTINGS_MODULE=server.conf.settings
python -c "
import django
django.setup()
from django.contrib.auth import get_user_model
from evennia.accounts.models import AccountDB

# Create superuser if doesn't exist
if not AccountDB.objects.filter(id=1).exists():
    superuser = AccountDB.objects.create_superuser(
        username='Admin',
        email='admin@witcher-rpg.local',
        password='changeme123'
    )
    print(f'Superuser created: {superuser.username}')
    print('Password: changeme123')
    print('CHANGE THIS PASSWORD IMMEDIATELY AFTER FIRST LOGIN!')
else:
    print('Superuser already exists')
"
```

**Security Note**: Change the admin password immediately after first login using:
```
password <old_password> = <new_password>
```

### Step 2: Verify Database

```bash
# Check all migrations are applied
export DJANGO_SETTINGS_MODULE=server.conf.settings
python -c "
import django
django.setup()
from django.db import connection

# Show applied migrations
from django.db.migrations.recorder import MigrationRecorder
migrations = MigrationRecorder.Migration.objects.all()
print(f'Total migrations applied: {migrations.count()}')

# Check key data
from world.witcher_rpg.item_models import ItemTemplate
from world.witcher_rpg.models import Vocation, CharacterSkill

print(f'Items in database: {ItemTemplate.objects.count()}')
print(f'Vocations: {Vocation.objects.count()}')
print(f'Skills: {CharacterSkill.objects.count()}')
"
```

Expected output:
- Total migrations: 50+ (core Evennia + 21 witcher_rpg)
- Items: 40 (weapons, armor, shields)
- Vocations: 8 (Witcher, Mage, Knight, Mercenary, Bard, Artisan, Ranger, Spy)
- Skills: 30+ (depends on seed data)

### Step 3: Start the Server

```bash
# Start server and portal
evennia start

# Check status
evennia status

# View logs (in separate terminal)
evennia --log

# To stop server
evennia stop

# To restart/reload
evennia reload
```

### Step 4: Access the Game

**Web Client** (Recommended for first test):
- Open browser to: http://localhost:4001
- Should see the new Witcher-themed landing page
- Click "Enter the World" to access web client

**Traditional MUD Client**:
- Host: localhost
- Port: 4000
- Connect with any MUD client (TinTin++, MUSHclient, etc.)

**Admin Panel**:
- URL: http://localhost:4001/admin/
- Login with superuser credentials
- Access all Django admin interfaces

---

## Part 2: System Testing Checklist

### 2.1 Character Creation System

**Test Steps**:
1. Login as superuser (Admin account)
2. Create a test character:
   ```
   requestchar <name>
   ```
3. Follow prompts to select:
   - Vocation (try Witcher or Knight first)
   - Country (Temeria, Redania, etc.)
   - Background (commoner, noble, etc.)
   - Distribute attribute points (Body, Reflex, Int, Will, Luck)
   - Choose skills from available list

**Expected Results**:
- ✅ Character request submitted
- ✅ Request appears in `gmrequests`
- ✅ Character not playable until approved
- ✅ All vocations available

**GM Approval Test**:
```
gmrequests          # View all pending requests
approvereq 1        # Approve first request
```

**Switch to Character**:
```
ic <character_name>
```

**Verify Character**:
```
sheet               # View character sheet
skills              # View skills
inventory           # Check starting inventory
```

### 2.2 Combat System Test

**Setup** (as GM):
1. Create a test dummy or enemy:
   ```
   @create Test Dummy
   @set Test Dummy/body = 5
   @set Test Dummy/reflex = 5
   ```

**Test Combat**:
```
combatstart Test Dummy              # Initiate combat

# Try different actions:
stance defensive                     # Change stance
attack Test Dummy                    # Basic attack
attack Test Dummy with sword         # Attack with specific weapon
cast Test Dummy with Igni           # Cast spell (if Mage/Witcher)

combatstatus                        # View combat state
```

**Expected Results**:
- ✅ Combat encounter starts
- ✅ Turn-based system works
- ✅ Damage calculated based on stats + weapon
- ✅ Stances affect combat modifiers
- ✅ Health tracking works
- ✅ Combat ends when HP reaches 0

**Test Weapons** (from new content):
```
# In admin panel or Django shell, give character a weapon:
# Then equip and use in combat

equip Iron Sword                    # Equip weapon
attack Test Dummy                   # Should use equipped weapon damage
```

### 2.3 Inventory & Equipment System

**Test Equipment Slots**:
```
inventory                           # View all items

# Test equipping to different slots:
equip <weapon> main                 # Main hand weapon
equip <weapon> off                  # Off-hand weapon
equip <shield>                      # Shield slot
equip <armor>                       # Auto-detect armor slot
equip <helmet>                      # Head slot

# View equipped:
equipment                           # Or whatever command shows equipped items

# Unequip:
unequip <item>
```

**Expected Results**:
- ✅ Items equip to correct slots
- ✅ Can't equip two 2-handed weapons
- ✅ Shield conflicts with off-hand weapon (if designed that way)
- ✅ Armor provides protection value
- ✅ Weapons affect combat damage

### 2.4 Shop System Test

**Create Test Shop** (as GM in admin or via commands):
```
# Use Django admin to create a shop:
# - Shop name: "Temerian Weaponsmith"
# - Type: weaponsmith
# - Tier: 2
# - Add ItemTemplates to shop inventory
```

**Test Shopping**:
```
browse                              # List available shops
browse <shop_name>                  # Browse shop inventory
buy <item> from <shop>              # Purchase item
sell <item> to <shop>               # Sell item
haggle <shop> for <item>            # Attempt to haggle price
```

**Expected Results**:
- ✅ Shop displays items with prices
- ✅ Purchase deducts gold, adds item to inventory
- ✅ Sell adds gold, removes item
- ✅ Haggle uses social stats
- ✅ Shop tier affects available items

### 2.5 Crafting System Test

**Setup** (recipes should already exist from migration 0018):
```
recipes                             # View available recipes
```

**Test Crafting**:
```
# Give character materials (via admin or GM commands)
# Then attempt crafting:

craft <recipe_name>                 # Attempt to craft item
crafthistory                        # View crafting history
setbonus                            # View available item sets
```

**Expected Results**:
- ✅ Recipe list displays
- ✅ Craft attempt checks materials
- ✅ Success creates item (if integrated)
- ✅ XP awarded based on vocation
- ✅ History tracks attempts

### 2.6 Communication System Test

**Test Paging**:
```
# Connect with two accounts/characters

# From Character A:
+page Character B = Hello!
+afk Testing AFK status
+busy Working on code

# From Character B:
+page Character A = Hi there!
+pagehistory                        # View message history
+ph                                 # Short form
```

**Test Channels**:
```
+channels                           # List available channels

# Default channels should exist
public Hello everyone!              # Send to public channel
```

**Test Organization Channels** (as GM):
```
# Create an organization in admin
# Create channel for organization:
+channelcreate House Foltest = org:House Foltest

# Add character to organization (via admin):
# Character should auto-subscribe to channel

# Test sending:
House Foltest Greetings, House Foltest!
```

**Expected Results**:
- ✅ Pages send and receive correctly
- ✅ Page history stores last 50 messages
- ✅ AFK/Busy status displays when paging
- ✅ Public channel works
- ✅ Org channels auto-subscribe on join
- ✅ Org channels auto-unsubscribe on leave
- ✅ Access control works (can't access wrong org channels)

### 2.7 Advancement System Test

**Test XP Spending**:
```
sheet                               # Check current XP
advance body                        # Advance attribute
advance blades                      # Advance skill
history                             # View advancement history
```

**Test Request System**:
```
request I want to learn Sign magic  # Submit GM request
myrequests                          # View own requests

# As GM:
gmrequests                          # View all requests
viewreq 1                           # View specific request
approvereq 1                        # Approve request
denyreq 2 = Not appropriate         # Deny with reason
```

**Expected Results**:
- ✅ XP costs calculated correctly
- ✅ Vocation multipliers applied
- ✅ Can't advance without enough XP
- ✅ Request system tracks submissions
- ✅ GM can approve/deny requests
- ✅ Players get notifications

### 2.8 Organization & Income System

**Test Organizations**:
```
orgs                                # List organizations
orginfo House Foltest               # View org details
orgjoin House Foltest               # Request to join
orgmembers House Foltest            # View members

# As GM or org leader:
orgapprove <character>              # Approve membership
orgkick <character>                 # Remove member

# Test income:
income                              # View income sources
incomecollect                       # Collect income
```

**Expected Results**:
- ✅ Organizations list correctly
- ✅ Join requests work
- ✅ Approval/kick updates membership
- ✅ Auto-subscribe/unsubscribe to org channel works
- ✅ Income calculated based on memberships
- ✅ MUSH formatting displays correctly

### 2.9 Front Page Test

**Test Website**:
1. Open browser to http://localhost:4001
2. Verify landing page displays with:
   - ✅ Hero section with game title
   - ✅ Dark fantasy Witcher-themed styling
   - ✅ Gold/amber color scheme
   - ✅ Server statistics (players online, etc.)
   - ✅ Feature showcase (6 cards)
   - ✅ Vocations grid (8 vocations)
   - ✅ Getting started steps
   - ✅ Responsive design (test on mobile size)
   - ✅ "Enter the World" button links to webclient
   - ✅ Smooth animations and hover effects

3. Test navigation:
   - ✅ Click "Enter the World" → Web client loads
   - ✅ Scroll navigation smooth
   - ✅ All sections visible

### 2.10 MUSH Formatting Test

**Test Token Rendering**:
```
# Use org commands that use MUSH formatting:
orginfo House Foltest               # Should show formatted output
income                              # Should use %r for line breaks

# Test in descriptions:
@desc me = This is a test.%rLine 2%rLine 3
look me                             # Verify formatting
```

**Expected Results**:
- ✅ %r creates line breaks
- ✅ %t creates tabs/indentation
- ✅ Color codes work (%cr, %cg, etc.)
- ✅ Web client displays formatting correctly
- ✅ Traditional client displays formatting correctly

---

## Part 3: GM/Admin Tools Testing

### Admin Panel Access

**URL**: http://localhost:4001/admin/

**Test Admin Interfaces**:
1. **Character Management**:
   - View all characters
   - Edit character stats
   - View character skills
   - Check character requests

2. **Item Management**:
   - Browse ItemTemplates (should see 40 items)
   - View items by category (weapon, armor, shield)
   - Check weapon types link to skills
   - Verify equipment slots assigned

3. **Shop Management**:
   - Create/edit shops
   - Add items to shop inventory
   - Set shop tiers and types

4. **Organization Management**:
   - Create organizations
   - Manage memberships
   - Set income values

5. **Crafting Management**:
   - View/edit recipes
   - Manage item sets
   - Check crafting history

**Expected Results**:
- ✅ All models accessible
- ✅ CRUD operations work
- ✅ Relationships display correctly
- ✅ Search and filters function
- ✅ Inline editing available

---

## Part 4: Load Testing (Optional)

### Basic Load Test

**Test with multiple connections**:
```bash
# In separate terminals, connect multiple times:
# Terminal 1:
evennia --dummyrunner 5             # Connect 5 dummy players

# Monitor server performance:
evennia status
tail -f server/logs/server.log
```

**Expected Results**:
- ✅ Server handles multiple connections
- ✅ No errors in logs
- ✅ Commands process in reasonable time
- ✅ Memory usage stable

---

## Part 5: Known Issues & Limitations

### Current Limitations

1. **Item Creation on Craft**:
   - Crafting logs success but may not create actual InventoryItem
   - Workaround: GM can create items via admin panel

2. **Material Checking**:
   - Craft command may not verify materials in inventory
   - Workaround: Track materials manually

3. **Workshop Locations**:
   - Craft command may not verify workshop requirement
   - Workaround: Honor system or GM enforcement

4. **Set Bonuses**:
   - Displays all sets but doesn't auto-detect equipped pieces
   - Workaround: Manual calculation by GM

5. **Combat AI**:
   - NPCs may need manual control by GM
   - Workaround: GM narrates NPC actions

### Workarounds & Manual Processes

**Giving Items to Players** (as GM):
```python
# Via Django shell:
export DJANGO_SETTINGS_MODULE=server.conf.settings
python -c "
import django
django.setup()
from evennia.objects.models import ObjectDB
from world.witcher_rpg.item_models import ItemTemplate

# Get character
char = ObjectDB.objects.get(db_key='CharacterName')

# Get item template
template = ItemTemplate.objects.get(name='Iron Sword')

# Create item in character's inventory
# (Implementation depends on inventory system)
print(f'Give {template.name} to {char.name}')
"
```

---

## Part 6: Pre-Launch Checklist

### Before Opening to Players

- [ ] Create GM accounts for all staff
- [ ] Set appropriate permissions/locks
- [ ] Populate shops with starting inventory
- [ ] Create starting areas/rooms
- [ ] Test character approval workflow
- [ ] Document any house rules
- [ ] Create helpfiles for players
- [ ] Set up backup schedule
- [ ] Test all critical systems
- [ ] Create announcement channels
- [ ] Prepare welcome messages
- [ ] Set up logging/monitoring

### Configuration Check

**server/conf/settings.py**:
```python
# Verify these settings:
SERVERNAME = "Witcher: The Northern Kingdoms"
INSTALLED_APPS includes "world.witcher_rpg"

# Set for production:
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'localhost']
SECRET_KEY = '<generate-new-secret-key>'

# Email settings (for password reset):
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# Configure SMTP settings
```

---

## Part 7: Troubleshooting

### Common Issues

**Issue**: Can't create superuser
```bash
# Solution: Use Django shell directly
export DJANGO_SETTINGS_MODULE=server.conf.settings
python -c "
import django
django.setup()
from evennia.accounts.models import AccountDB
AccountDB.objects.create_superuser('Admin', 'admin@local', 'password123')
"
```

**Issue**: Migrations not applied
```bash
# Solution: Run migrations with settings module
export DJANGO_SETTINGS_MODULE=server.conf.settings
python -c "
import django
django.setup()
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate'])
"
```

**Issue**: Server won't start
```bash
# Check logs:
cat server/logs/server.log
cat server/logs/portal.log

# Verify database:
ls -lh server/evennia.db3

# Test connection:
python -c "import django; django.setup(); from evennia.accounts.models import AccountDB; print(AccountDB.objects.count())"
```

**Issue**: Front page not loading
```bash
# Collect static files:
evennia collectstatic --noinput

# Verify templates exist:
ls -la web/templates/website/
ls -la web/static/website/css/
```

---

## Part 8: Next Steps After Testing

### If All Tests Pass

1. **Document any issues found**
2. **Fix critical bugs**
3. **Gather feedback from testers**
4. **Create player documentation**
5. **Set up production environment**
6. **Plan soft launch schedule**

### Recommended Additions

1. **More Content**:
   - Additional weapons/armor for all tiers
   - Consumable items (potions, food)
   - Crafting materials
   - Quest items

2. **More Rooms**:
   - Starting cities for each country
   - Wilderness areas
   - Dungeons/combat areas
   - Social hubs

3. **NPCs**:
   - Shop keepers
   - Quest givers
   - Combat trainers
   - Faction leaders

4. **Quests/Missions**:
   - Starter quests for each vocation
   - Faction storylines
   - GM-run events

5. **Documentation**:
   - In-game helpfiles
   - Newbie guide
   - Command reference
   - Lore documents

---

## Part 9: Testing Completion Report Template

After testing, document your findings:

```markdown
# Testing Report - [Date]

## Systems Tested
- [ ] Character Creation: [PASS/FAIL] - Notes:
- [ ] Combat System: [PASS/FAIL] - Notes:
- [ ] Inventory/Equipment: [PASS/FAIL] - Notes:
- [ ] Shop System: [PASS/FAIL] - Notes:
- [ ] Crafting System: [PASS/FAIL] - Notes:
- [ ] Communication: [PASS/FAIL] - Notes:
- [ ] Advancement: [PASS/FAIL] - Notes:
- [ ] Organizations: [PASS/FAIL] - Notes:
- [ ] Front Page: [PASS/FAIL] - Notes:
- [ ] MUSH Formatting: [PASS/FAIL] - Notes:

## Critical Issues Found
1.
2.
3.

## Minor Issues Found
1.
2.
3.

## Recommended Fixes
1.
2.
3.

## Ready for Launch? [YES/NO]
Reasoning:

## Next Steps
1.
2.
3.
```

---

## Contact & Support

- **Evennia Documentation**: https://www.evennia.com/docs/
- **Evennia Discord**: https://discord.gg/AJJpcRUhtF
- **Issue Tracker**: [Your GitHub repo if applicable]

---

## Appendix: Quick Reference Commands

### Server Management
```bash
evennia start          # Start server
evennia stop           # Stop server
evennia reload         # Reload server (keeps connections)
evennia reboot         # Full restart
evennia status         # Check status
evennia --log          # View live logs
evennia migrate        # Run migrations
```

### Player Commands
```
requestchar            # Request character
sheet                  # View character
skills                 # View skills
inventory              # View inventory
equipment              # View equipped items
combatstart <target>   # Start combat
+page <char> = <msg>   # Send page
+channels              # List channels
browse <shop>          # Browse shop
buy <item>             # Buy item
craft <recipe>         # Craft item
advance <stat>         # Spend XP
```

### GM Commands
```
gmrequests             # View all requests
approvereq <id>        # Approve request
denyreq <id>           # Deny request
+channelcreate         # Create channel
shopmanage             # Manage shops
learnrecipe            # Teach recipe
@create                # Create object
@set                   # Set attribute
@grant                 # Grant permission
```

---

**Good luck with your launch! May your dice rolls be high and your bugs be few. 🎲⚔️**
