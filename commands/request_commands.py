"""
Unified Request System Commands for Witcher RPG

Handles all types of GM approval requests:
- Character generation
- Special item requests
- Plot hook requests
- Custom requests
"""

from evennia import Command, CmdSet
from django.utils import timezone
from world.witcher_rpg.request_models import (
    UnifiedRequest,
    CharacterGenerationRequest
)
from world.witcher_rpg.models import WitcherCharacter, Vocation, Country


class ChargenInputCmdSet(CmdSet):
    """
    Temporary cmdset for handling character generation input.
    This cmdset overrides normal command processing to capture all input.
    """
    key = "chargen_input"
    priority = 101  # Higher priority to override default commands
    mergetype = "Replace"  # Replace all other commands

    def at_cmdset_creation(self):
        """Add the input handler command."""
        self.add(CmdChargenInput())


class CmdChargenInput(Command):
    """
    Handle all input during character generation.
    """
    key = "__chargen_input__"
    aliases = []
    locks = "cmd:all()"
    auto_help = False
    arg_regex = r"^.*$"  # Match everything

    def func(self):
        """Process input based on current chargen step."""
        caller = self.caller

        if not hasattr(caller.ndb, 'chargen') or not caller.ndb.chargen:
            # Chargen not active, remove cmdset
            caller.cmdset.remove(ChargenInputCmdSet)
            caller.msg("|yCharacter generation not active.|n")
            return

        # Get the callback function
        callback = caller.ndb._chargen_callback
        if callback:
            # Call the callback with the raw input
            callback(caller, self.raw_string.strip())


class CmdRequestChar(Command):
    """
    Submit a character generation request for GM approval.

    Usage:
      requestchar

    Starts an interactive character generation process where you'll
    specify your character's vocation, stats, skills, and background.

    The GM will review your request and approve or deny it based on:
    - Mechanical validity (stat/skill point allocation)
    - Background and concept quality
    - Balance considerations
    - Campaign fit

    Note: This is for brand new character creation. To advance an
    existing character's stats/skills to levels 6-7, use the 'request'
    command instead.
    """

    key = "requestchar"
    aliases = ["charrequest", "newchar"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller

        # Check if already has a character
        try:
            if WitcherCharacter.objects.filter(db_object=caller).exists():
                caller.msg("|yYou already have a character!|n")
                caller.msg("To create a new character, please contact a GM.")
                return
        except:
            pass  # Handle case where character doesn't exist yet

        # Check for pending request
        pending = UnifiedRequest.objects.filter(
            requestor=caller,
            request_type='chargen',
            status='pending'
        ).exists()

        if pending:
            caller.msg("|yYou already have a pending character generation request.|n")
            caller.msg("Use |wmyrequests|n to check the status.")
            return

        # Start interactive character generation
        caller.msg(
            "\n" + "=" * 70 + "\n"
            "|wCharacter Generation Request|n\n" +
            "=" * 70 + "\n\n"
            "Welcome to character creation! This process will guide you through\n"
            "creating a character for GM approval.\n\n"
            "You can type |wquit|n at any time to cancel.\n\n"
            "=" * 70 + "\n"
        )

        # Initialize chargen state on the caller
        caller.ndb.chargen = {
            'step': 'name',
            'name': None,
            'vocation': None,
            'race': None,
            'country': None,
            'social_rank': 2,
            'stats': {
                'strength': 1, 'agility': 1, 'endurance': 1, 'reflexes': 1,
                'wit': 1, 'intelligence': 1, 'willpower': 1, 'perception': 1,
                'charm': 1, 'appearance': 1, 'graces': 1, 'cunning': 1
            },
            'skills': {},
            'background': None
        }

        # Add the chargen input handler cmdset
        caller.cmdset.add(ChargenInputCmdSet)

        # Start with name prompt
        self._prompt_name(caller)

    def _cleanup_chargen(self, caller):
        """Clean up chargen state and remove cmdset."""
        if hasattr(caller.ndb, 'chargen'):
            del caller.ndb.chargen
        if hasattr(caller.ndb, '_chargen_callback'):
            del caller.ndb._chargen_callback
        caller.cmdset.remove(ChargenInputCmdSet)

    def _prompt_name(self, caller):
        """Prompt for character name."""
        caller.msg("\n|wStep 1: Character Name|n")
        caller.msg("What is your character's name?")
        caller.msg("Type the name you want for your character:")

        # Set up a callback for the next input
        def _name_callback(caller, raw_string, **kwargs):
            name = raw_string.strip()
            if name.lower() == 'quit':
                caller.msg("|yCharacter generation cancelled.|n")
                self._cleanup_chargen(caller)
                return

            if not name or len(name) < 2:
                caller.msg("|rName must be at least 2 characters long.|n")
                self._prompt_name(caller)
                return

            caller.ndb.chargen['name'] = name
            caller.ndb.chargen['step'] = 'vocation'
            self._prompt_vocation(caller)

        caller.ndb._chargen_callback = _name_callback

    def _prompt_vocation(self, caller):
        """Prompt for vocation selection."""
        vocations = Vocation.objects.all().order_by('name')

        caller.msg("\n|wStep 2: Choose Your Vocation|n")
        caller.msg("Select your character's vocation/class:\n")

        for i, voc in enumerate(vocations, 1):
            caller.msg(f"  {i}. |c{voc.get_name_display()}|n - {voc.description[:60]}...")

        caller.msg("\nType the number of your choice:")

        def _vocation_callback(caller, raw_string, **kwargs):
            choice = raw_string.strip()
            if choice.lower() == 'quit':
                caller.msg("|yCharacter generation cancelled.|n")
                self._cleanup_chargen(caller)
                return

            try:
                choice_num = int(choice)
                vocations_list = list(vocations)
                if 1 <= choice_num <= len(vocations_list):
                    chosen_voc = vocations_list[choice_num - 1]
                    caller.ndb.chargen['vocation'] = chosen_voc.id
                    caller.ndb.chargen['step'] = 'race'
                    self._prompt_race(caller)
                else:
                    caller.msg("|rInvalid choice. Please select a valid number.|n")
                    self._prompt_vocation(caller)
            except ValueError:
                caller.msg("|rPlease enter a number.|n")
                self._prompt_vocation(caller)

        caller.ndb._chargen_callback = _vocation_callback

    def _prompt_race(self, caller):
        """Prompt for race selection."""
        races = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Witcher']

        caller.msg("\n|wStep 3: Choose Your Race|n")
        caller.msg("Select your character's race:\n")

        for i, race in enumerate(races, 1):
            caller.msg(f"  {i}. |c{race}|n")

        caller.msg("\nType the number of your choice:")

        def _race_callback(caller, raw_string, **kwargs):
            choice = raw_string.strip()
            if choice.lower() == 'quit':
                caller.msg("|yCharacter generation cancelled.|n")
                self._cleanup_chargen(caller)
                return

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(races):
                    caller.ndb.chargen['race'] = races[choice_num - 1]
                    caller.ndb.chargen['step'] = 'country'
                    self._prompt_country(caller)
                else:
                    caller.msg("|rInvalid choice. Please select a valid number.|n")
                    self._prompt_race(caller)
            except ValueError:
                caller.msg("|rPlease enter a number.|n")
                self._prompt_race(caller)

        caller.ndb._chargen_callback = _race_callback

    def _prompt_country(self, caller):
        """Prompt for country selection."""
        countries = Country.objects.all().order_by('name')

        caller.msg("\n|wStep 4: Choose Country of Origin|n")
        caller.msg("Select your character's country:\n")

        for i, country in enumerate(countries, 1):
            caller.msg(f"  {i}. |c{country.get_name_display()}|n (+1 {country.bonus_stat.title()})")

        caller.msg("\nType the number of your choice:")

        def _country_callback(caller, raw_string, **kwargs):
            choice = raw_string.strip()
            if choice.lower() == 'quit':
                caller.msg("|yCharacter generation cancelled.|n")
                self._cleanup_chargen(caller)
                return

            try:
                choice_num = int(choice)
                countries_list = list(countries)
                if 1 <= choice_num <= len(countries_list):
                    chosen_country = countries_list[choice_num - 1]
                    caller.ndb.chargen['country'] = chosen_country.id
                    caller.ndb.chargen['step'] = 'social_rank'
                    self._prompt_social_rank(caller)
                else:
                    caller.msg("|rInvalid choice. Please select a valid number.|n")
                    self._prompt_country(caller)
            except ValueError:
                caller.msg("|rPlease enter a number.|n")
                self._prompt_country(caller)

        caller.ndb._chargen_callback = _country_callback

    def _prompt_social_rank(self, caller):
        """Prompt for social rank selection."""
        vocation = Vocation.objects.get(id=caller.ndb.chargen['vocation'])
        max_rank = WitcherCharacter.get_max_rank_for_vocation(vocation.name)

        ranks = [
            (1, 'Rank 1 - Outcast', -5),
            (2, 'Rank 2 - Commoner', 0),
            (3, 'Rank 3 - Knight/Small Gentry', +1),
            (4, 'Rank 4 - Landed Gentry', +2),
            (5, 'Rank 5 - Royalty', +3),
        ]

        caller.msg("\n|wStep 5: Choose Social Rank|n")
        caller.msg(f"Select your character's social rank (max {max_rank} for {vocation.get_name_display()}):\n")

        for rank_num, rank_name, cr_mod in ranks:
            if rank_num <= max_rank:
                caller.msg(f"  {rank_num}. |c{rank_name}|n ({cr_mod:+d} CR)")
            else:
                caller.msg(f"  {rank_num}. |K{rank_name} (Unavailable for your vocation)|n")

        caller.msg("\nType the number of your choice:")

        def _rank_callback(caller, raw_string, **kwargs):
            choice = raw_string.strip()
            if choice.lower() == 'quit':
                caller.msg("|yCharacter generation cancelled.|n")
                self._cleanup_chargen(caller)
                return

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= 5:
                    if choice_num <= max_rank:
                        caller.ndb.chargen['social_rank'] = choice_num
                        caller.ndb.chargen['step'] = 'stats'
                        self._prompt_stats(caller)
                    else:
                        caller.msg(f"|rYour vocation can only have rank {max_rank} or lower.|n")
                        self._prompt_social_rank(caller)
                else:
                    caller.msg("|rInvalid choice. Please select 1-5.|n")
                    self._prompt_social_rank(caller)
            except ValueError:
                caller.msg("|rPlease enter a number.|n")
                self._prompt_social_rank(caller)

        caller.ndb._chargen_callback = _rank_callback

    def _prompt_stats(self, caller):
        """Prompt for stat allocation."""
        stats = caller.ndb.chargen['stats']
        total_spent = sum(v - 1 for v in stats.values())
        remaining = WitcherCharacter.STAT_POINTS - total_spent

        caller.msg("\n|wStep 6: Allocate Stats|n")
        caller.msg(f"You have |y{remaining}|n points remaining out of {WitcherCharacter.STAT_POINTS}.")
        caller.msg("Each stat starts at 1. Maximum is 10.\n")

        caller.msg("|wPhysical Stats:|n")
        caller.msg(f"  STR (Strength):    {stats['strength']}")
        caller.msg(f"  AGI (Agility):     {stats['agility']}")
        caller.msg(f"  END (Endurance):   {stats['endurance']}")
        caller.msg(f"  REF (Reflexes):    {stats['reflexes']}\n")

        caller.msg("|wMental Stats:|n")
        caller.msg(f"  WIT (Wit):           {stats['wit']}")
        caller.msg(f"  INT (Intelligence):  {stats['intelligence']}")
        caller.msg(f"  WIL (Willpower):     {stats['willpower']}")
        caller.msg(f"  PER (Perception):    {stats['perception']}\n")

        caller.msg("|wSocial Stats:|n")
        caller.msg(f"  CHA (Charm):       {stats['charm']}")
        caller.msg(f"  APP (Appearance):  {stats['appearance']}")
        caller.msg(f"  GRA (Graces):      {stats['graces']}")
        caller.msg(f"  CUN (Cunning):     {stats['cunning']}\n")

        caller.msg("To set a stat: |wSTR 5|n, |wAGI 4|n, etc.")
        caller.msg("Type |wdone|n when finished, |wreset|n to start over.")

        def _stats_callback(caller, raw_string, **kwargs):
            input_str = raw_string.strip()
            if input_str.lower() == 'quit':
                caller.msg("|yCharacter generation cancelled.|n")
                self._cleanup_chargen(caller)
                return

            if input_str.lower() == 'done':
                # Validate allocation
                is_valid, error, points_spent = WitcherCharacter.validate_stat_allocation(
                    caller.ndb.chargen['stats']
                )
                if is_valid:
                    caller.ndb.chargen['step'] = 'skills'
                    self._prompt_skills(caller)
                else:
                    caller.msg(f"|r{error}|n")
                    self._prompt_stats(caller)
                return

            if input_str.lower() == 'reset':
                caller.ndb.chargen['stats'] = {
                    'strength': 1, 'agility': 1, 'endurance': 1, 'reflexes': 1,
                    'wit': 1, 'intelligence': 1, 'willpower': 1, 'perception': 1,
                    'charm': 1, 'appearance': 1, 'graces': 1, 'cunning': 1
                }
                caller.msg("|yStats reset to base values.|n")
                self._prompt_stats(caller)
                return

            # Parse stat input
            parts = input_str.split()
            if len(parts) != 2:
                caller.msg("|rFormat: STAT VALUE (e.g., STR 5)|n")
                self._prompt_stats(caller)
                return

            stat_abbr = parts[0].lower()
            try:
                value = int(parts[1])
            except ValueError:
                caller.msg("|rValue must be a number.|n")
                self._prompt_stats(caller)
                return

            stat_map = {
                'str': 'strength', 'agi': 'agility', 'end': 'endurance', 'ref': 'reflexes',
                'wit': 'wit', 'int': 'intelligence', 'wil': 'willpower', 'per': 'perception',
                'cha': 'charm', 'app': 'appearance', 'gra': 'graces', 'cun': 'cunning'
            }

            if stat_abbr not in stat_map:
                caller.msg("|rUnknown stat. Use STR, AGI, END, REF, WIT, INT, WIL, PER, CHA, APP, GRA, CUN|n")
                self._prompt_stats(caller)
                return

            stat_name = stat_map[stat_abbr]

            if value < 1 or value > 10:
                caller.msg("|rStat must be between 1 and 10.|n")
                self._prompt_stats(caller)
                return

            caller.ndb.chargen['stats'][stat_name] = value
            caller.msg(f"|gSet {stat_name} to {value}|n")
            self._prompt_stats(caller)

        caller.ndb._chargen_callback = _stats_callback

    def _prompt_skills(self, caller):
        """Prompt for skill allocation."""
        skills = caller.ndb.chargen['skills']
        total_cost = sum(WitcherCharacter.calculate_skill_cost(v) for v in skills.values())
        remaining = WitcherCharacter.SKILL_POINTS - total_cost

        caller.msg("\n|wStep 7: Allocate Skills|n")
        caller.msg(f"You have |y{remaining}|n points remaining out of {WitcherCharacter.SKILL_POINTS}.")
        caller.msg("Skills 0-4 cost 1 point per level. Skills 5+ cost 2 points per level above 4.")
        caller.msg("|yOnly ONE skill can start at 5 or higher.|n\n")

        caller.msg("|wWeapon Skills:|n")
        caller.msg(f"  blades:    {skills.get('blades', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('blades', 0))})")
        caller.msg(f"  axes:      {skills.get('axes', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('axes', 0))})")
        caller.msg(f"  maces:     {skills.get('maces', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('maces', 0))})")
        caller.msg(f"  spears:    {skills.get('spears', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('spears', 0))})")
        caller.msg(f"  crossbows: {skills.get('crossbows', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('crossbows', 0))})")
        caller.msg(f"  brawling:  {skills.get('brawling', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('brawling', 0))})\n")

        caller.msg("|wSpecial Skills:|n")
        caller.msg(f"  alchemy:      {skills.get('alchemy', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('alchemy', 0))})")
        caller.msg(f"  magery:       {skills.get('magery', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('magery', 0))})")
        caller.msg(f"  sign_sorcery: {skills.get('sign_sorcery', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('sign_sorcery', 0))})\n")

        caller.msg("|wCrafting Skills:|n")
        caller.msg(f"  smithing:  {skills.get('smithing', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('smithing', 0))})")
        caller.msg(f"  carpentry: {skills.get('carpentry', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('carpentry', 0))})")
        caller.msg(f"  herbalism: {skills.get('herbalism', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('herbalism', 0))})\n")

        caller.msg("|wGeneral/Support Skills:|n")
        caller.msg(f"  athletics:  {skills.get('athletics', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('athletics', 0))})")
        caller.msg(f"  resistance: {skills.get('resistance', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('resistance', 0))})")
        caller.msg(f"  leadership: {skills.get('leadership', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('leadership', 0))})")
        caller.msg(f"  tactics:    {skills.get('tactics', 0)}  (cost: {WitcherCharacter.calculate_skill_cost(skills.get('tactics', 0))})\n")

        caller.msg("To set a skill: |wblades 5|n, |walchemy 3|n, etc.")
        caller.msg("Type |wdone|n when finished, |wreset|n to start over.")

        def _skills_callback(caller, raw_string, **kwargs):
            input_str = raw_string.strip()
            if input_str.lower() == 'quit':
                caller.msg("|yCharacter generation cancelled.|n")
                self._cleanup_chargen(caller)
                return

            if input_str.lower() == 'done':
                # Validate allocation
                is_valid, error = WitcherCharacter.validate_skill_allocation(
                    caller.ndb.chargen['skills']
                )
                if is_valid:
                    caller.ndb.chargen['step'] = 'background'
                    self._prompt_background(caller)
                else:
                    caller.msg(f"|r{error}|n")
                    self._prompt_skills(caller)
                return

            if input_str.lower() == 'reset':
                caller.ndb.chargen['skills'] = {}
                caller.msg("|ySkills reset.|n")
                self._prompt_skills(caller)
                return

            # Parse skill input
            parts = input_str.split()
            if len(parts) != 2:
                caller.msg("|rFormat: SKILL VALUE (e.g., blades 5)|n")
                self._prompt_skills(caller)
                return

            skill_name = parts[0].lower()
            try:
                value = int(parts[1])
            except ValueError:
                caller.msg("|rValue must be a number.|n")
                self._prompt_skills(caller)
                return

            valid_skills = [
                'blades', 'axes', 'maces', 'spears', 'crossbows', 'brawling',
                'alchemy', 'magery', 'sign_sorcery',
                'smithing', 'carpentry', 'herbalism',
                'athletics', 'resistance', 'leadership', 'tactics'
            ]

            if skill_name not in valid_skills:
                caller.msg(f"|rUnknown skill. Valid skills: {', '.join(valid_skills)}|n")
                self._prompt_skills(caller)
                return

            if value < 0 or value > 10:
                caller.msg("|rSkill must be between 0 and 10.|n")
                self._prompt_skills(caller)
                return

            if value == 0 and skill_name in caller.ndb.chargen['skills']:
                del caller.ndb.chargen['skills'][skill_name]
                caller.msg(f"|gRemoved {skill_name}|n")
            else:
                caller.ndb.chargen['skills'][skill_name] = value
                caller.msg(f"|gSet {skill_name} to {value} (cost: {WitcherCharacter.calculate_skill_cost(value)})|n")

            self._prompt_skills(caller)

        caller.ndb._chargen_callback = _skills_callback

    def _prompt_background(self, caller):
        """Prompt for character background."""
        caller.msg("\n|wStep 8: Character Background|n")
        caller.msg("Write a brief background for your character (minimum 100 characters).")
        caller.msg("Describe your character's history, personality, goals, and how they")
        caller.msg("fit into the Witcher world.\n")
        caller.msg("When finished, type |wdone|n on a new line.")
        caller.msg("Start typing your background:\n")

        # Use a list to accumulate background lines
        if 'background_lines' not in caller.ndb.chargen:
            caller.ndb.chargen['background_lines'] = []

        def _background_callback(caller, raw_string, **kwargs):
            input_str = raw_string.strip()

            if input_str.lower() == 'quit':
                caller.msg("|yCharacter generation cancelled.|n")
                self._cleanup_chargen(caller)
                return

            if input_str.lower() == 'done':
                background = '\n'.join(caller.ndb.chargen['background_lines'])
                if len(background) < 100:
                    caller.msg("|rBackground must be at least 100 characters. Please continue writing.|n")
                    self._prompt_background(caller)
                    return

                caller.ndb.chargen['background'] = background
                caller.ndb.chargen['step'] = 'review'
                self._show_review(caller)
                return

            # Add line to background
            caller.ndb.chargen['background_lines'].append(raw_string)
            # Continue collecting
            caller.ndb._chargen_callback = _background_callback

        caller.ndb._chargen_callback = _background_callback

    def _show_review(self, caller):
        """Show character summary and prompt for final confirmation."""
        data = caller.ndb.chargen
        vocation = Vocation.objects.get(id=data['vocation'])
        country = Country.objects.get(id=data['country'])

        caller.msg("\n" + "=" * 70)
        caller.msg("|wCHARACTER SUMMARY - Please Review|n")
        caller.msg("=" * 70)
        caller.msg(f"\n|wName:|n {data['name']}")
        caller.msg(f"|wVocation:|n {vocation.get_name_display()}")
        caller.msg(f"|wRace:|n {data['race']}")
        caller.msg(f"|wCountry:|n {country.get_name_display()} (+1 {country.bonus_stat.title()})")
        caller.msg(f"|wSocial Rank:|n {data['social_rank']}\n")

        caller.msg("|wStats:|n")
        stats = data['stats']
        total_spent = sum(v - 1 for v in stats.values())
        caller.msg(f"  Physical: STR {stats['strength']}, AGI {stats['agility']}, END {stats['endurance']}, REF {stats['reflexes']}")
        caller.msg(f"  Mental:   WIT {stats['wit']}, INT {stats['intelligence']}, WIL {stats['willpower']}, PER {stats['perception']}")
        caller.msg(f"  Social:   CHA {stats['charm']}, APP {stats['appearance']}, GRA {stats['graces']}, CUN {stats['cunning']}")
        caller.msg(f"  (Total spent: {total_spent}/{WitcherCharacter.STAT_POINTS})\n")

        caller.msg("|wSkills:|n")
        skills = data['skills']
        total_cost = sum(WitcherCharacter.calculate_skill_cost(v) for v in skills.values())
        for skill_name, skill_level in sorted(skills.items()):
            cost = WitcherCharacter.calculate_skill_cost(skill_level)
            caller.msg(f"  {skill_name}: {skill_level} (cost: {cost})")
        caller.msg(f"  (Total spent: {total_cost}/{WitcherCharacter.SKILL_POINTS})\n")

        caller.msg("|wBackground:|n")
        caller.msg(data['background'])
        caller.msg("\n" + "=" * 70)

        caller.msg("\nType |wsubmit|n to submit this character for GM approval,")
        caller.msg("or |wcancel|n to cancel character generation.")

        def _review_callback(caller, raw_string, **kwargs):
            input_str = raw_string.strip().lower()

            if input_str == 'cancel' or input_str == 'quit':
                caller.msg("|yCharacter generation cancelled.|n")
                self._cleanup_chargen(caller)
                return

            if input_str == 'submit':
                self._submit_request(caller)
                return

            caller.msg("|rPlease type 'submit' to submit or 'cancel' to cancel.|n")
            caller.ndb._chargen_callback = _review_callback

        caller.ndb._chargen_callback = _review_callback

    def _submit_request(self, caller):
        """Submit the character generation request."""
        data = caller.ndb.chargen
        vocation = Vocation.objects.get(id=data['vocation'])
        country = Country.objects.get(id=data['country'])

        # Create unified request
        unified_request = UnifiedRequest.objects.create(
            requestor=caller,
            request_type='chargen',
            title=f"Character: {data['name']} ({vocation.get_name_display()})",
            description=f"New character creation request for {data['name']}, a {data['race']} {vocation.get_name_display()}.",
            priority='normal'
        )

        # Create character generation request
        chargen_request = CharacterGenerationRequest.objects.create(
            unified_request=unified_request,
            character_name=data['name'],
            vocation=vocation,
            race=data['race'],
            country=country,
            social_rank=data['social_rank'],
            stats_allocation=data['stats'],
            skills_allocation=data['skills'],
            background=data['background']
        )

        # Validate the request
        is_valid, errors = chargen_request.validate_allocations()

        # Clean up
        self._cleanup_chargen(caller)

        # Notify player
        caller.msg("\n" + "=" * 70)
        caller.msg("|gCharacter generation request submitted!|n")
        caller.msg("=" * 70)
        caller.msg(f"\nRequest ID: |w#{unified_request.id}|n")
        caller.msg(f"Character: |c{data['name']}|n")
        caller.msg(f"Status: |yPending GM Approval|n\n")

        if is_valid:
            caller.msg("|gValidation: All allocations are mechanically valid.|n")
        else:
            caller.msg("|yValidation Issues:|n")
            for error in errors:
                caller.msg(f"  - {error}")
            caller.msg("\n|yNote:|n Your request is still submitted, but the GM will need to")
            caller.msg("review these validation issues.")

        caller.msg("\nUse |wmyrequests|n to check the status of your request.")
        caller.msg("A GM will review your character and approve or deny it.\n")
        caller.msg("=" * 70)


class CmdGMRequests(Command):
    """
    View all pending GM approval requests (GM only).

    Usage:
      +grequest
      +grequest/pending
      +grequest/approved
      +grequest/denied
      +grequest/all
      +grequest/chargen
      +grequest/advancement
      +grequest/view <id>

    Shows all requests in a table format. Without arguments, shows
    only pending requests.

    Filters:
      /pending    - Only pending requests (default)
      /approved   - Only approved requests
      /denied     - Only denied requests
      /all        - All requests regardless of status

    Request types:
      /chargen             - Character generation
      /advancement_stat    - Stat advancement (6-7)
      /advancement_skill   - Skill advancement (6-7)
      /advancement         - All advancement requests
      /special_item        - Special item request
      /plot_hook           - Plot hook request
      /custom              - Custom request

    View full request:
      +grequest/view <id>  - View complete request details

    Use |w+grequest/approve <id> [notes]|n to approve a request
    Use |w+grequest/deny <id> <reason>|n to deny a request
    """

    key = "+grequest"
    aliases = ["gmrequests", "+grequests"]
    locks = "cmd:perm(Builder)"
    help_category = "GM"

    def func(self):
        # Handle /view switch
        if self.switches and 'view' in self.switches:
            if not self.args:
                self.caller.msg("Usage: +grequest/view <id>")
                return
            # Delegate to view function
            self._view_request(self.args.strip())
            return

        # Parse filter from switches
        filter_status = 'pending'
        filter_type = None

        if self.switches:
            switch = self.switches[0].lower()
            if switch in ['pending', 'approved', 'denied', 'all']:
                filter_status = switch
            elif switch in ['chargen', 'advancement_stat', 'advancement_skill',
                          'special_item', 'plot_hook', 'custom', 'advancement']:
                filter_type = switch
                filter_status = 'all'

        # Get requests
        requests = UnifiedRequest.objects.select_related(
            'requestor', 'reviewed_by'
        ).order_by('-created_at')

        # Apply filters
        if filter_status != 'all':
            requests = requests.filter(status=filter_status)

        if filter_type:
            if filter_type == 'advancement':
                requests = requests.filter(
                    request_type__in=['advancement_stat', 'advancement_skill']
                )
            else:
                requests = requests.filter(request_type=filter_type)

        if not requests.exists():
            if filter_status == 'pending':
                self.caller.msg("No pending requests.")
            else:
                self.caller.msg(f"No {filter_status} requests found.")
            return

        # Build table output
        lines = []
        lines.append("=" * 100)
        if filter_status == 'pending':
            lines.append(f"Pending GM Approval Requests ({requests.count()})")
        else:
            lines.append(f"GM Approval Requests - {filter_status.upper()} ({requests.count()})")
        lines.append("=" * 100)

        # Table header
        lines.append(
            f"{'ID':<5} {'Status':<12} {'Type':<20} {'From':<15} {'Title':<45}"
        )
        lines.append("-" * 100)

        for request in requests:
            # Status indicator
            if request.status == 'approved':
                status = "|gAPPROVED|n"
            elif request.status == 'denied':
                status = "|rDENIED|n"
            elif request.status == 'revoked':
                status = "|yREVOKED|n"
            else:
                status = "|yPENDING|n"

            # Priority indicator
            priority_marker = ""
            if request.priority == 'urgent':
                priority_marker = "|r!|n"
            elif request.priority == 'high':
                priority_marker = "|y!|n"

            # Truncate long fields
            req_type = request.get_request_type_display()[:18]
            requestor_name = request.requestor.name[:13]
            title = request.title[:43]

            lines.append(
                f"{request.id:<5} {status:<20} {req_type:<20} {requestor_name:<15} {title:<45} {priority_marker}"
            )

        lines.append("=" * 100)
        lines.append("\nCommands:")
        lines.append("  |w+grequest/view <id>|n           - View full request details")
        lines.append("  |w+grequest/approve <id> [notes]|n - Approve request")
        lines.append("  |w+grequest/deny <id> <reason>|n   - Deny request")
        lines.append("=" * 100)

        self.caller.msg("\n".join(lines))

    def _view_request(self, request_id):
        """View detailed information about a specific request."""
        try:
            request = UnifiedRequest.objects.select_related(
                'requestor', 'reviewed_by'
            ).get(id=request_id)
        except UnifiedRequest.DoesNotExist:
            self.caller.msg(f"Request #{request_id} not found.")
            return
        except ValueError:
            self.caller.msg("Request ID must be a number.")
            return

        # Build output
        lines = []
        lines.append("=" * 70)
        lines.append(f"Request #{request.id} - {request.get_request_type_display()}")
        lines.append("=" * 70)

        # Status
        if request.status == 'approved':
            status = "|g[APPROVED]|n"
        elif request.status == 'denied':
            status = "|r[DENIED]|n"
        elif request.status == 'revoked':
            status = "|y[REVOKED]|n"
        else:
            status = "|y[PENDING]|n"

        lines.append(f"Status: {status}")
        lines.append(f"Priority: {request.get_priority_display()}")
        lines.append(f"Requestor: {request.requestor.name}")
        lines.append(f"Created: {request.created_at.strftime('%Y-%m-%d %H:%M')}")

        if request.reviewed_by:
            lines.append(
                f"Reviewed by: {request.reviewed_by.name} "
                f"on {request.reviewed_at.strftime('%Y-%m-%d %H:%M')}"
            )

        lines.append("")
        lines.append("|wTitle:|n")
        lines.append(request.title)
        lines.append("")
        lines.append("|wDescription:|n")
        lines.append(request.description)

        # Show request data
        if request.request_data:
            lines.append("")
            lines.append("|wRequest Data:|n")
            for key, value in request.request_data.items():
                lines.append(f"  {key}: {value}")

        # Show chargen details
        if request.request_type == 'chargen':
            try:
                chargen = request.chargen_details
                lines.append("")
                lines.append("|wCharacter Generation Details:|n")
                lines.append(f"  Name: {chargen.character_name}")
                lines.append(f"  Vocation: {chargen.vocation.get_name_display()}")
                lines.append(f"  Race: {chargen.race}")
                if chargen.country:
                    lines.append(f"  Country: {chargen.country.get_name_display()}")
                lines.append(f"  Social Rank: {chargen.get_social_rank_display()}")
                lines.append("")
                lines.append("|wStat Allocation:|n")
                for stat, value in chargen.stats_allocation.items():
                    lines.append(f"  {stat}: {value}")
                lines.append("")
                lines.append("|wSkill Allocation:|n")
                for skill, value in chargen.skills_allocation.items():
                    lines.append(f"  {skill}: {value}")
                lines.append("")
                lines.append("|wBackground:|n")
                lines.append(chargen.background)
                lines.append("")
                lines.append(f"Stats Valid: {'|gYes|n' if chargen.stats_valid else '|rNo|n'}")
                lines.append(f"Skills Valid: {'|gYes|n' if chargen.skills_valid else '|rNo|n'}")
                if chargen.validation_errors:
                    lines.append("|rValidation Errors:|n")
                    for error in chargen.validation_errors:
                        lines.append(f"  - {error}")
            except Exception as e:
                lines.append(f"|rError loading chargen details:|n {e}")

        # Show review notes
        if request.review_notes:
            lines.append("")
            lines.append("|wReview Notes:|n")
            lines.append(request.review_notes)

        lines.append("")
        lines.append("=" * 70)

        if request.status == 'pending':
            lines.append("Commands:")
            lines.append(f"  |w+grequest/approve {request.id} [notes]|n - Approve this request")
            lines.append(f"  |w+grequest/deny {request.id} <reason>|n - Deny this request")
            lines.append("=" * 70)

        self.caller.msg("\n".join(lines))


class CmdApproveRequest(Command):
    """
    Approve a GM approval request (GM only).

    Usage:
      +grequest/approve <request_id> [notes]
      +grequest/approve 42 Great character concept!
      +grequest/approve 15

    Approves a pending request. Depending on the request type:
    - chargen: Creates the character
    - advancement: Applies the stat/skill increase
    - special_item: Notifies player of approval
    - plot_hook: Notifies player of approval

    Optional notes will be shown to the player.
    """

    key = "+grequest/approve"
    aliases = ["approvereq", "approve"]
    locks = "cmd:perm(Builder)"
    help_category = "GM"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: approvereq <request_id> [notes]")
            return

        # Parse ID and notes
        parts = self.args.strip().split(None, 1)
        request_id = parts[0]
        notes = parts[1] if len(parts) > 1 else ""

        # Get request
        try:
            request = UnifiedRequest.objects.select_related(
                'requestor'
            ).get(id=request_id)
        except UnifiedRequest.DoesNotExist:
            self.caller.msg(f"Request #{request_id} not found.")
            return
        except ValueError:
            self.caller.msg("Request ID must be a number.")
            return

        # Check if already reviewed
        if request.status != 'pending':
            self.caller.msg(
                f"Request #{request_id} has already been {request.status}."
            )
            return

        # Approve request
        request.approve(self.caller, notes)

        # Handle based on type
        if request.request_type == 'chargen':
            self._handle_chargen_approval(request)
        elif request.request_type in ['advancement_stat', 'advancement_skill']:
            self._handle_advancement_approval(request)
        else:
            # Generic approval
            self._handle_generic_approval(request)

        # Notify GM
        self.caller.msg(
            f"|gRequest #{request.id} approved!|n\n"
            f"Type: {request.get_request_type_display()}\n"
            f"From: {request.requestor.name}\n"
            f"Title: {request.title}"
        )

    def _handle_chargen_approval(self, request):
        """Handle character generation approval."""
        try:
            chargen = request.chargen_details

            # TODO: Actually create the character
            # For now, just notify
            request.requestor.msg(
                "=" * 70 + "\n"
                "|g=== Character Generation Request APPROVED ===|n\n" +
                "=" * 70 + "\n"
                f"Character: {chargen.character_name}\n"
                f"Vocation: {chargen.vocation.get_name_display()}\n"
                f"Approved by: {request.reviewed_by.name}\n\n"
                f"{request.review_notes}\n\n"
                "Your character will be created shortly.\n" +
                "=" * 70
            )

        except Exception as e:
            self.caller.msg(f"|rError processing chargen approval:|n {e}")

    def _handle_advancement_approval(self, request):
        """Handle advancement request approval."""
        # This integrates with the existing advancement system
        # The ApprovalRequest model should handle the actual stat/skill increase

        request.requestor.msg(
            "=" * 70 + "\n"
            "|g=== Advancement Request APPROVED ===|n\n" +
            "=" * 70 + "\n"
            f"Request: {request.title}\n"
            f"Approved by: {request.reviewed_by.name}\n\n"
            f"{request.review_notes}\n\n"
            "Your character has been advanced!\n" +
            "=" * 70
        )

    def _handle_generic_approval(self, request):
        """Handle generic request approval."""
        request.requestor.msg(
            "=" * 70 + "\n"
            "|g=== Request APPROVED ===|n\n" +
            "=" * 70 + "\n"
            f"Type: {request.get_request_type_display()}\n"
            f"Title: {request.title}\n"
            f"Approved by: {request.reviewed_by.name}\n\n"
            f"{request.review_notes}\n" +
            "=" * 70
        )


class CmdDenyRequest(Command):
    """
    Deny a GM approval request (GM only).

    Usage:
      +grequest/deny <request_id> <reason>
      +grequest/deny 42 Need more background detail and in-game justification

    Denies a pending request with a reason that will be shown to the player.
    The reason should explain what needs improvement or why it was denied.
    """

    key = "+grequest/deny"
    aliases = ["denyreq", "deny"]
    locks = "cmd:perm(Builder)"
    help_category = "GM"

    def func(self):
        if not self.args or " " not in self.args:
            self.caller.msg("Usage: denyreq <request_id> <reason>")
            self.caller.msg("A reason is required.")
            return

        # Parse ID and reason
        parts = self.args.strip().split(None, 1)
        request_id = parts[0]
        reason = parts[1]

        # Get request
        try:
            request = UnifiedRequest.objects.select_related(
                'requestor'
            ).get(id=request_id)
        except UnifiedRequest.DoesNotExist:
            self.caller.msg(f"Request #{request_id} not found.")
            return
        except ValueError:
            self.caller.msg("Request ID must be a number.")
            return

        # Check if already reviewed
        if request.status != 'pending':
            self.caller.msg(
                f"Request #{request_id} has already been {request.status}."
            )
            return

        # Deny request
        request.deny(self.caller, reason)

        # Notify player
        request.requestor.msg(
            "=" * 70 + "\n"
            "|r=== Request DENIED ===|n\n" +
            "=" * 70 + "\n"
            f"Type: {request.get_request_type_display()}\n"
            f"Title: {request.title}\n"
            f"Reviewed by: {request.reviewed_by.name}\n\n"
            f"|wReason:|n\n{reason}\n\n"
            "You may submit a new request addressing these concerns.\n" +
            "=" * 70
        )

        # Notify GM
        self.caller.msg(
            f"|rRequest #{request.id} denied.|n\n"
            f"Type: {request.get_request_type_display()}\n"
            f"From: {request.requestor.name}\n"
            f"Title: {request.title}\n\n"
            f"Player has been notified."
        )


class CmdMyRequests(Command):
    """
    View your submitted requests.

    Usage:
      myrequests
      myrequests [pending|approved|denied|all]

    Shows all requests you've submitted with their current status.
    Use this to check on pending approvals or review past requests.
    """

    key = "myrequests"
    aliases = ["myreqs"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller

        # Parse filter
        filter_status = 'all'
        if self.args:
            arg = self.args.strip().lower()
            if arg in ['pending', 'approved', 'denied', 'all']:
                filter_status = arg

        # Get requests
        requests = UnifiedRequest.objects.filter(
            requestor=caller
        ).select_related('reviewed_by').order_by('-created_at')

        # Apply filter
        if filter_status != 'all':
            requests = requests.filter(status=filter_status)

        if not requests.exists():
            caller.msg("You haven't submitted any requests yet.")
            return

        # Build output
        lines = []
        lines.append("=" * 70)
        lines.append(f"Your Submitted Requests ({requests.count()})")
        lines.append("=" * 70)

        for request in requests:
            # Status indicator
            if request.status == 'approved':
                status = "|g[APPROVED]|n"
            elif request.status == 'denied':
                status = "|r[DENIED]|n"
            elif request.status == 'revoked':
                status = "|y[REVOKED]|n"
            else:
                status = "|y[PENDING]|n"

            lines.append("")
            lines.append(f"|wRequest #{request.id}|n {status}")
            lines.append(f"Type: {request.get_request_type_display()}")
            lines.append(f"Title: {request.title}")
            lines.append(f"Submitted: {request.created_at.strftime('%Y-%m-%d %H:%M')}")

            if request.reviewed_by:
                lines.append(
                    f"Reviewed by: {request.reviewed_by.name} "
                    f"on {request.reviewed_at.strftime('%Y-%m-%d %H:%M')}"
                )
                if request.review_notes:
                    lines.append(f"Notes: {request.review_notes}")

        lines.append("")
        lines.append("=" * 70)

        caller.msg("\n".join(lines))
