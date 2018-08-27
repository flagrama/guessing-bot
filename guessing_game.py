"""This module provides an interface for running a guessing game."""
import logging
from datetime import datetime, timedelta
from collections import deque

from database.streamer import Streamer
from database.participant import Participant

class GuessingGame():
    """This is a class for running a guessing game."""
    def __init__(self, streamer):
        """The constructor for GuessingGame class."""
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.streamer = streamer
        self.running = False
        self.freebie = None
        self.commands = ['!guess', '!hud', '!guesspoints']
        self.guesses = {
            "item": deque(),
            "medal": deque(),
            "song": deque()
        }
        self.guessables = {
            "dungeons": [
                'deku', 'dodongo', 'jabu',
                'forest', 'fire', 'water', 'shadow', 'spirit', 'light'
            ],
            "songs": [
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
        }

        self.logger.setLevel(logging.DEBUG)

    def do_command(self, user, permissions, command):
        """
        The function to parse a command.

        Parameters:
            username (dict): A dictionary containing the username and user_id of the sender
            permissions( dict): A dictionary containing the user permissions of the sender
            command (string[]): A list containing the command and its arguments
        """
        try:
            command_name = command[0].lower()
            if (command_name == '!guesspoints'
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self._set_guess_points(command)

            if command_name == '!guess':
                if len(command) > 2:
                    subcommand_name = command[1].lower()
                    command_value = command[2:]
                    if subcommand_name == 'medal':
                        return self._do_medal_guess(user, command_value)
                command_value = command[1].lower()
                item = self.parse_item(command_value)
                self._do_item_guess(user, item)

            if (command_name == '!hud'
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                command_value = command[1].lower()
                item = self.parse_item(command_value)
                return self._complete_guess(item, user['channel-id'])
        except IndexError:
            self.logger.error('Command missing arguments')
        return None

    def _complete_guess(self, item, channel):
        if not item:
            self.logger.info('Item %s not found', item)
            return
        expiration = datetime.now() - timedelta(minutes=15)
        first_guess = False
        participant = None
        streamer = None
        for guess in self.guesses['item']:
            if guess['timestamp'] < expiration:
                continue
            if guess['guess'] is not item:
                continue
            try:
                streamer = Streamer.objects.get( #pylint: disable=no-member
                    channel_id=channel, participants__user_id=guess['user-id'])
                if streamer.participants:
                    participant = streamer.participants[0]
            except Streamer.DoesNotExist: #pylint: disable=no-member
                participant = Participant(
                    username=guess['username'],
                    user_id=guess['user-id'],
                    session_points=0,
                    total_points=0)
                self.streamer.participants.append(participant)
                self.streamer.save()
                self.streamer.reload()
                streamer = Streamer.objects.get( #pylint: disable=no-member
                    channel_id=channel, participants__user_id=guess['user-id'])
                participant = streamer.participants[0]
                self.logger.error('Participant with ID %s does not exist in the database',
                                  guess['user-id'])
            if not first_guess:
                self.logger.info('User %s made the first correct guess', guess['username'])
                first_guess = True
            for update_participant in streamer.participants:
                update_participant.session_points += self.streamer.points
                update_participant.total_points += self.streamer.points
            self.logger.info('User %s guessed correctly and earned %s points',
                             guess['username'], self.streamer.points)
        streamer.save()
        streamer.reload()
        self.guesses['item'] = deque()
        self.logger.info('Guesses completed')

    def _set_guess_points(self, command):
        try:
            command_value = command[1].lower()
            if int(command_value) > 0:
                message = 'Set points value to %s' % command_value
                self.streamer.points = command_value
                self.streamer.save()
                self.logger.info(message)
                return message
            message = 'Cannot set points value lower than 0'
            self.logger.info(message)
            return message
        except ValueError:
            message = 'Cannot convert %s to an integer' % command_value
            self.logger.error(message)
            return message

    def _do_item_guess(self, user, item):
        if not item:
            self.logger.info('Item %s not found', item)
            return
        self._remove_stale_guesses(self.guesses['item'], user['username'])
        now = datetime.now()
        guess = {
            "timestamp": now,
            "user-id": user['user-id'],
            "username": user['username'],
            "guess": item
        }
        self.guesses['item'].append(guess)
        self.logger.info('%s Item %s guessed by user %s', now, item, user['username'])
        self.logger.debug(self.guesses['item'])

    def _do_medal_guess(self, user, medals):
        if len(medals) < 5 or len(medals) < 6 and not self.freebie:
            self.logger.info('Medal command incomplete')
            self.logger.debug(medals)
            return
        self._remove_stale_guesses(self.guesses['medal'], user['username'])
        medal_guess = {
            "forest": None,
            "fire": None,
            "water": None,
            "shadow": None,
            "spirit": None,
            "light": None
        }
        i = 0
        for medal in medal_guess:
            guess = medals[i].lower()
            if guess not in self.guessables['dungeons'] and guess != 'pocket':
                self.logger.info('Invalid medal %s', guess)
                return
            if medal == self.freebie or guess == 'pocket':
                continue
            medal_guess[medal] = guess
            i += 1
        medal_guess['username'] = user['username']
        medal_guess['timestamp'] = datetime.now()
        self.guesses['medal'].append(medal_guess)
        self.logger.debug(medal_guess)

    @staticmethod
    def _remove_stale_guesses(guess_queue, username):
        new_queue = deque()
        expiration = datetime.now() - timedelta(minutes=15)
        for guess in guess_queue:
            if guess['timestamp'] < expiration:
                continue
            if guess['username'] == username:
                continue
            new_queue.append(guess)
        guess_queue = new_queue

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
