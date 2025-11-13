# Commands to Fix GameMaster and Create OOC Room

Run these commands in-game as GameMaster:

## Step 1: Create OOC Room

```
@dig OOC Lobby
```

Note the room number (e.g., #12345), then:

```
@desc OOC Lobby = |w=== Welcome to The Northern Kingdoms ===|n%r%rYou are in the Out of Character (OOC) lobby. This is where new players create their characters before entering the game world.%r%r|yTo create a character:|n%r  Type |wrequestchar|n to start the interactive character creation process. You'll choose your vocation, race, stats, skills, and write a background. A Game Master will review and approve your character.%r%r|yTo check your requests:|n%r  Type |wmyrequests|n to see the status of your character request.%r%r|yAvailable commands:|n%r  |wlook|n     - Look around%r  |wwho|n      - See who's online%r  |whelp|n     - Get help%r  |wquit|n     - Disconnect%r%rOnce your character is approved, you'll automatically enter the game world in Vengerberg. Welcome to the Witcher RPG!
```

## Step 2: Set OOC Room Typeclass

```
@typeclass OOC Lobby = typeclasses.rooms.OOCRoom
```

## Step 3: Create GameMaster Character

```
@charcreate GameMaster = typeclasses.characters.WitcherCharacter
```

## Step 4: Teleport Character and Link It

```
@tel GameMaster = Vengerberg Central Market Square
@ic GameMaster
```

## Step 5: Update Settings

Edit `server/conf/settings.py` and add (replace <OOC_ROOM_ID> with actual number from Step 1):

```python
START_LOCATION = "#<OOC_ROOM_ID>"
DEFAULT_HOME = "#<OOC_ROOM_ID>"
```

## Step 6: Reload

```
@reload
```

That's it!
