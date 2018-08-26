"""This module provides an interface for running a guessing game."""
import logging
from datetime import datetime, timedelta
from collections import deque

class GuessingGame():
    """This is a class for running a guessing game."""
    def __init__(self):
        """The constructor for GuessingGame class."""
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.commands = ['!guess', '!hud']
        self.guesses = deque()
        self.medals = [
            'forest', 'fire', 'water', 'spirit', 'shadow', 'light'
        ]
        self.songs = [
            'lullaby', 'zelda', 'zeldas',
            'saria', 'sarias',
            'epona', 'eponas',
            'sunsong', 'sun', 'suns',
            'songoftime', 'time', 'sot',
            'songofstorms', 'storm', 'storms', 'sos',
            'minuet', 'greenote',
            'bolero', 'rednote',
            'serenade', 'bluenote',
            'requiem', 'orangenote',
            'nocturne', 'purplenote',
            'prelude', 'yellownote'
        ]

        self.logger.setLevel(logging.DEBUG)

    def do_command(self, username, command):
        """
        The function to parse a command.

        Parameters:
            command (string[]): A list of the command and its arguments
        """
        try:
            command_name = command[0].lower()
            command_value = command[1].lower()

            if command_name == '!guess':
                item = self.parse_item(command_value)
                if not item:
                    self.logger.info('Item %s not found', command_value)
                    return
                self._remove_stale_guesses(username)
                now = datetime.now()
                guess = {
                    "timestamp": now,
                    "username": username,
                    "guess": item
                }
                self.guesses.append(guess)
                self.logger.info('%s Item %s guessed by user %s', now, item, username)
                self.logger.debug(self.guesses)

            if command_name == '!hud':
                item = self.parse_item(command_value)
                if not item:
                    self.logger.info('Item %s not found', command_value)
                    return
                expiration = datetime.now() - timedelta(minutes=15)
                first_guess = False
                for guess in self.guesses:
                    if guess['timestamp'] < expiration:
                        continue
                    if guess['guess'] is not item:
                        continue
                    if not first_guess:
                        self.logger.info('User %s made the first correct guess', username)
                        first_guess = True
                    self.logger.info('User %s guessed correctly', username)
                self.guesses = deque()
                self.logger.info('Guesses completed')
        except IndexError:
            self.logger.error('Command missing arguments')

    def _remove_stale_guesses(self, username):
        new_queue = deque()
        expiration = datetime.now() - timedelta(minutes=15)
        for guess in self.guesses:
            if guess['timestamp'] < expiration:
                continue
            if guess['username'] == username:
                continue
            new_queue.append(guess)
        self.guesses = new_queue

    # Integrate with the database in the future
    @staticmethod
    def parse_item(item):
        """
        Return the internal item name based on user provided string.

        Parameters:
            item (string): A code word for an item name.

        Returns:
            string: A string which contains the internal item name
        """
        if item in ['bow']:
            return 'Bow'
        if item in ['slingshot', 'seedbag']:
            return 'Slingshot'
        if item in ['nut', 'nuts', 'dekunuts']:
            return 'Deku Nuts'
        if item in ['agony', 'stoneofagony', 'stone', 'pieseed']:
            return 'Stone of Agony'
        if item in ['firearrow', 'firearrows', 'farrow', 'farrows']:
            return 'Fire Arrows'
        if item in ['icearrow', 'icearrows', 'iarrow', 'iarrows']:
            return 'Ice Arrows'
        if item in ['lightarrow', 'lightarrows', 'larrow', 'larrows']:
            return 'Light Arrows'
        if item in ['beans', 'magicbeans']:
            return 'Magic Beans'
        if item in ['sticks', 'dekusticks', 'stick', 'dekustick']:
            return 'Deku Sticks'
        if item in ['bombs', 'bombbag', 'bomb']:
            return 'Bomb Bag'
        if item in ['boomerang', 'boomer', 'rang', 'banana']:
            return 'Boomerang'
        if item in ['hookshot', 'hs', 'longshot', 'ls']:
            return 'Hookshot'
        if item in ['bombchu', 'bombchus', 'chus']:
            return 'Bombchus'
        if item in ['lens', 'lensoftruth', 'lot']:
            return 'Lens of Truth'
        if item in ['dinsfire', 'dins', 'din']:
            return 'Din\'s Fire'
        if item in ['faroreswind', 'farores', 'farore', 'fw']:
            return 'Farore\'s Wind'
        if item in ['nayruslove', 'nayrus', 'nayru', 'condom']:
            return 'Nayru\'s Love'
        if item in ['sword1', 'kokirisword']:
            return 'Kokiri Sword'
        if item in ['sword3', 'biggoronsword', 'biggoron', 'bgs']:
            return 'Biggoron Sword'
        if item in ['shield3', 'mirrorshield', 'mirror', 'mshield']:
            return 'Mirror Shield'
        if item in ['gorontunic', 'redtunic']:
            return 'Goron Tunic'
        if item in ['zoratunic', 'bluetunic']:
            return 'Zora Tunic'
        if item in ['ironboots', 'iboots', 'iron', 'irons']:
            return 'Iron Boots'
        if item in ['hoverboots', 'hboots', 'hover', 'hovers']:
            return 'Hover Boots'
        if item in ['hammer', 'megaton', 'megatonhammer']:
            return 'Megaton Hammer'
        if item in ['ocarina', 'fairyocarina', 'flute', 'oot']:
            return 'Ocarina'
        if item in ['bottle', 'rutonote', 'ruto']:
            return 'Bottle'
        if item in [
                'bracelet', 'lift',
                'silvergauntlets', 'lift2', 'silvers', 'silver', 'silvergaunt',
                'goldgauntlets', 'lift3', 'golds', 'golden', 'goldgaunt'
            ]:
            return 'Strength Upgrade'
        if item in ['silverscale', 'scale', 'goldscale', 'scale2']:
            return 'Diving Scale'
        if item in ['wallet']:
            return 'Wallet'
        if item in ['magic', 'doublemagic', 'magic2']:
            return 'Magic'
        if item in ['greenrupee']:
            return 'Validation'
        if item in ['childegg', 'kidtrade', 'kidegg', 'weird', 'weirdegg']:
            return 'Weird Egg'
        if item in [
                'adultegg', 'adulttrade', 'pocketegg',
                'adultcucco', 'pocketcucco',
                'cojiro', 'bluecucco',
                'mushroom', 'oddmushroom',
                'oddpotion', 'oddpoultice', 'potion',
                'saw', 'poachersaw',
                'brokensword',
                'perscription', 'script',
                'frog', 'eyeballfrog', 'eyeball',
                'eyedrops', 'drops',
                'claim', 'claimcheck'
            ]:
            return 'Adult Trade Item'
        return None
