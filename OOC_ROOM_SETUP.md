# OOC Room & Character Auto-Creation Setup

## Implementation Complete

The following has been successfully implemented:

1. **OOCRoom Typeclass** (`typeclasses/rooms.py`)
   - Restricts commands to basic navigation + character creation
   - Auto-adds OOC command set when created
   - Includes welcoming description for new players

2. **OOC Command Set** (`commands/ooc_commands.py`)
   - Only allows: `look`, `who`, `quit`, `help`, `requestchar`, `myrequests`
   - Replaces all other commands to prevent IC actions

3. **Character Auto-Creation** (`commands/request_commands.py`)
   - When GM approves character with `+grequest/approve <id>`:
     - Creates Character object (Evennia entity)
     - Creates CharacterStats with allocated stats
     - Creates CharacterSkills with allocated skills
     - Creates WitcherCharacter linking everything
     - Sets location to Vengerberg Central Market Square (#595)
     - Links character to account
     - Notifies player when ready

4. **Account Login Flow** (`typeclasses/accounts.py`)
   - New accounts without characters: stay in OOC lobby
   - Existing accounts with characters: auto-puppet character

## Next Steps - Manual Setup Required

### Step 1: Create the OOC Room

Log into the game as a Builder/Admin and run:

```
@py from world.create_ooc_room import create_ooc_room; create_ooc_room()
```

This will create the OOC Lobby room and display its dbref (e.g., `#12345`).

### Step 2: Update Settings

Edit `server/conf/settings.py` and add (replacing `<OOC_ROOM_ID>` with the actual dbref):

```python
# Starting location for new accounts
START_LOCATION = "#<OOC_ROOM_ID>"

# Fallback/home location
DEFAULT_HOME = "#<OOC_ROOM_ID>"
```

### Step 3: Reload Server

```bash
evennia reload
```

### Step 4: Test the System

1. **Test New Account Flow:**
   - Create a new test account
   - Should start in OOC Lobby
   - Only have access to basic commands
   - Run `requestchar` to test character creation

2. **Test Character Creation:**
   - Complete the requestchar process
   - Submit a character request
   - As GM, run `+grequest` to see the request
   - Approve it with `+grequest/approve <id> Great character!`
   - Character should be auto-created
   - Player should be able to use `ic <character_name>` to enter game

3. **Test Returning Account:**
   - Disconnect and reconnect with account that has a character
   - Should auto-puppet the character
   - Should spawn in last location or Vengerberg

## Character Creation Flow

```
New Account Login
       ↓
   OOC Lobby (restricted commands)
       ↓
   requestchar (interactive process)
       ↓
   Submit Request → GM Approval Queue
       ↓
   GM reviews with +grequest/view <id>
       ↓
   GM approves with +grequest/approve <id>
       ↓
   Character Auto-Created:
   - Character object in Vengerberg
   - WitcherCharacter database record
   - Stats and skills applied
   - Linked to account
       ↓
   Player uses: ic <character_name>
       ↓
   Character enters game world
```

## Available GM Commands

- `+grequest` - View all pending requests
- `+grequest/view <id>` - View detailed request info
- `+grequest/approve <id> [notes]` - Approve and auto-create character
- `+grequest/deny <id> <reason>` - Deny with reason

## Available Player Commands (in OOC)

- `look` - Look around the OOC lobby
- `who` - See who's online
- `help` - Get help
- `quit` - Disconnect
- `requestchar` - Start character creation
- `myrequests` - Check request status

## File Changes Summary

**New Files:**
- `commands/ooc_commands.py` - OOC command set
- `world/create_ooc_room.py` - OOC room creation script
- `OOC_ROOM_SETUP.md` - This documentation

**Modified Files:**
- `typeclasses/rooms.py` - Added OOCRoom class
- `typeclasses/accounts.py` - Added at_post_login() hook
- `commands/request_commands.py` - Implemented _handle_chargen_approval()

## Troubleshooting

**Issue:** Can't create OOC room - circular import error
**Solution:** The room will be created when you run the @py command in-game after the server reload

**Issue:** Character creation fails
**Solution:** Check the error traceback. Most common issues:
- Vengerberg room #595 doesn't exist (will fallback to Limbo #2)
- Invalid stat/skill allocations in the request
- Missing vocation or country in database

**Issue:** Players can use IC commands in OOC
**Solution:** Make sure the OOC room has the command set added. Check with:
```
@examine <OOC room>=cmdset
```

**Issue:** Account doesn't start in OOC room
**Solution:** Verify START_LOCATION in settings.py and reload server

## Success Criteria

You'll know everything is working when:
1. New accounts spawn in OOC Lobby
2. They can only use basic commands + requestchar
3. They can complete character creation process
4. GM can approve and character is auto-created
5. Player can enter game with `ic <character_name>`
6. Returning players auto-puppet their character
