"""This module provides an interface for running a guessing game."""
import logging
from datetime import datetime, timedelta
from collections import deque

import jstyleson

from database.streamer import Streamer
from database.participant import Participant

class GuessingGame():
    """This is a class for running a guessing game."""
    def __init__(self, streamer):
        """The constructor for GuessingGame class."""
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.streamer = streamer
        self.commands = [
            '!guess', '!hud', '!points', '!guesspoints', '!firstguess', '!start', '!mode',
            '!modedel'
        ]
        self.guesses = {
            "item": deque(),
            "medal": deque(),
            "song": deque()
        }
        self.guessables = {
            "blacklist": [
                'Keys', 'Treasures', 'Skulls', 'Tokens', 'Prize', 'Label', 'Badge',
                'Heart Container', 'Pieces'
            ],
            "dungeons": [
                'deku', 'dodongo', 'jabu',
                'forest', 'fire', 'water', 'shadow', 'spirit', 'light'
            ],
            "songs": [
                "Zelda's Lullaby", "Saria's Song", "Epona's Song", "Sun's Song",
                "Song of Time", "Song of Storms", "Minuet of Forest", "Bolero of Fire",
                "Serenade of Water", "Requiem of Spirit", "Nocturne of Shadow", "Prelude of Light"
            ]
        }
        self.state = {
            "running": False,
            "freebie": None,
            "mode": [],
            "modes": [
                {
                    "name": "keysanity",
                    "items": ["Boss Key"]
                },
                {
                    "name": "songsanity",
                    "items": self.guessables['songs']
                },
                {
                    "name": "egg",
                    "items": ["Child Trade"]
                },
                {
                    "name": "ocarina",
                    "items": ["Ocarina"]
                }
            ]
        }

        with open('items.json') as items:
            self.items = jstyleson.load(items)

        self.logger.setLevel(logging.DEBUG)

    def do_command(self, user, permissions, command):
        """
        The function to parse a command.

        Parameters:
            user (dict): A dictionary containing the username and user_id of the sender
            permissions (dict): A dictionary containing the user permissions of the sender
            command (string[]): A list containing the command and its arguments

        Returns:
            Returns a string meant to be sent to Twitch chat. If a falsy value is returned
            no message is sent to chat.
        """
        try:
            command_name = command[0].lower()
            if (command_name == '!guesspoints'
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self._set_guess_points(command)

            if (command_name == '!firstguess'
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self._set_first_guess(command)

            if command_name == '!guess':
                return self._guess_command(command, user)

            if command_name == '!points':
                return self._points_command(command, user)

            if (command_name == '!mode'
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self._mode_command(command, user)

            if (command_name == '!modedel'
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self._modedel_command(command, user)

            if (command_name == '!hud'
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self._hud_command(command, user)

            if (command_name == '!start'
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self._start_guessing_game(user)
        except IndexError:
            self.logger.error('Command missing arguments')
        return None

    def _complete_guess(self, item, channel):
        if not self.state['running']:
            self.logger.info('Guessing game not running')
            return
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
                for update_participant in streamer.participants:
                    update_participant.session_points += self.streamer.first_bonus
                    update_participant.total_points += self.streamer.first_bonus
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

    def _do_points_check(self, channel, username):
        try:
            streamer = Streamer.objects.get( #pylint: disable=no-member
                channel_id=channel, participants__username=username)
            if streamer.participants:
                return '%s has %s points' % (username, streamer.participants[0].session_points)
        except Streamer.DoesNotExist: #pylint: disable=no-member
            self.logger.error('Participant with username %s does not exist in the database',
                              username)
        return None

    def _do_total_points_check(self, channel, username):
        try:
            streamer = Streamer.objects.get( #pylint: disable=no-member
                channel_id=channel, participants__username=username)
            if streamer.participants:
                return '%s has %s total points' % (username, streamer.participants[0].total_points)
        except Streamer.DoesNotExist: #pylint: disable=no-member
            self.logger.error('Participant with username %s does not exist in the database',
                              username)
        return None

    def _do_item_guess(self, user, item):
        if not item:
            self.logger.info('Item %s not found', item)
            return
        self.guesses['item'] = self._remove_stale_guesses(self.guesses['item'], user['username'])
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
        if len(medals) < 5 or len(medals) < 6 and not self.state['freebie']:
            self.logger.info('Medal command incomplete')
            self.logger.debug(medals)
            return
        self.guesses['medal'] = self._remove_stale_guesses(self.guesses['medal'], user['username'])
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
            if medal == self.state['freebie'] or guess == 'pocket':
                continue
            medal_guess[medal] = guess
            i += 1
        medal_guess['username'] = user['username']
        medal_guess['timestamp'] = datetime.now()
        self.guesses['medal'].append(medal_guess)
        self.logger.debug(medal_guess)

    def _set_guess_points(self, command):
        try:
            command_value = command[1].lower()
            if int(command_value) > 0:
                message = 'Set points value to %s' % command_value
                self.streamer.points = int(command_value)
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

    def _set_first_guess(self, command):
        try:
            command_value = command[1].lower()
            if int(command_value) > 0:
                message = 'Set first guess bonus to %s' % command_value
                self.streamer.first_bonus = int(command_value)
                self.streamer.save()
                self.logger.info(message)
                return message
            message = 'Cannot set first guess bonus lower than 0'
            self.logger.info(message)
            return message
        except ValueError:
            message = 'Cannot convert %s to an integer' % command_value
            self.logger.error(message)
            return message

    def _guess_command(self, command, user):
        if not self.state['running']:
            return None
        if len(command) > 2:
            subcommand_name = command[1].lower()
            command_value = command[2:]
            if subcommand_name == 'medal':
                return self._do_medal_guess(user, command_value)
        command_value = command[1].lower()
        item = self._parse_item(command_value)
        return self._do_item_guess(user, item)

    def _points_command(self, command, user):
        channel = user['channel-id']
        if len(command) == 1:
            return self._do_points_check(channel, user['username'])
        if len(command) == 2:
            if command[1] == 'total':
                return self._do_total_points_check(channel, user['username'])
            return self._do_points_check(channel, command[1])
        if len(command) == 3:
            if command[2] != 'total':
                return None
            return self._do_total_points_check(channel, command[1])
        return None

    def _mode_command(self, command, user):
        if self.state['running']:
            self.logger.info('Guessing game already started')
            return None
        if len(command) < 2:
            message = 'Mode command requires a mode argument'
            self.logger.info(message)
            return message
        mode = command[1]
        if mode == 'normal':
            message = 'Mode reset to normal by %s' % user['username']
            print(message)
            self.state['mode'].clear()
            self.logger.info(message)
            return message
        for modes in self.state['modes']:
            if mode in modes['name'] and mode not in self.state['mode']:
                message = 'Mode %s added by %s' % (mode, user['username'])
                self.state['mode'] += [mode]
                self.logger.info(message)
                return message
        return None

    def _modedel_command(self, command, user):
        if self.state['running']:
            self.logger.info('Guessing game already started')
            return None
        if len(command) < 2:
            message = 'Mode Delete command requires a mode argument'
            self.logger.info(message)
            return message
        mode = command[1]
        if mode in self.state['mode']:
            message = 'Mode %s removed by %s' % (mode, user['username'])
            self.state['mode'].remove(mode)
            self.logger.info(message)
            return message
        return None

    def _hud_command(self, command, user):
        if not self.state['running']:
            self.logger.info('Guessing game not running')
            return None
        if len(command) > 1:
            subcommand_name = command[1]
            if subcommand_name == 'reset':
                return self._end_guessing_game(user)
        command_value = command[1].lower()
        item = self._parse_item(command_value)
        return self._complete_guess(item, user['channel-id'])

    def _start_guessing_game(self, user):
        if self.state['running']:
            self.logger.info('Guessing game already running')
            return None
        self.state['running'] = True
        message = 'Guessing game started by %s' % user['username']
        self.logger.info(message)
        return message

    def _end_guessing_game(self, user):
        if not self.state['running']:
            self.logger.info('Guessing game not running')
            return None
        self.guesses['item'] = deque()
        self.guesses['medal'] = deque()
        self.guesses['song'] = deque()
        self.state['running'] = False
        self.state['freebie'] = None
        self.state['mode'].clear()
        for participant in self.streamer.participants:
            participant.session_points = 0
        self.streamer.save()
        self.streamer.reload()
        message = 'Guessing game ended by %s' % user['username']
        self.logger.info(message)
        return message

    def _check_items_allowed(self, item):
        if any(skip in item for skip in self.guessables['blacklist']):
            return False
        for modes in self.state['modes']:
            if modes['name'] not in self.state['mode'] and item in modes['items']:
                return False
        return True

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
        return new_queue

    # Integrate with the database in the future
    def _parse_item(self, guess):
        for item in self.items:
            if 'name' in item:
                if not self._check_items_allowed(item['name']):
                    continue
            if 'codes' in item:
                for code in item['codes'].split(','):
                    if guess in [code.strip()]:
                        return item['name']
            elif 'stages' in item:
                codes = []
                for stage in item['stages']:
                    if 'codes' in stage:
                        if any(code in stage['codes'].split(',') for code in codes):
                            continue
                        for code in stage['codes'].split(','):
                            codes += [code.strip()]
                if guess in codes:
                    return item['name']
        return None
