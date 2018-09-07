"""This module provides an interface for running a guessing game."""
import os.path
import errno
from datetime import datetime, timedelta
from collections import deque
from functools import partial
import csv

import boto3
import jstyleson

from database import Streamer, Participant, Session
import guessing
import whitelist_commands
import settings

class GuessingGame():
    """This is a class for running a guessing game."""
    def __init__(self, streamer):
        """The constructor for GuessingGame class."""
        self.logger = settings.init_logger(__name__)
        with open('items.json') as items:
            self.items = jstyleson.load(items)
        self.guesses = {
            "item": deque(),
            "medal": deque(),
            "song": deque()
        }
        self.state = {
            "running": False,
            "freebie": None,
            "mode": [],
            "songs": {},
            "medals": {},
            "modes": [
                {
                    "name": "keysanity",
                    "items": ["Boss Key"]
                },
                {
                    "name": "songsanity",
                    "items": []
                },
                {
                    "name": "egg",
                    "items": ["Child Trade"]
                },
                {
                    "name": "ocarina",
                    "items": ["Ocarina"]
                }
            ],
            "guessables": {
                "blacklist": [
                    'Keys', 'Treasures', 'Skulls', 'Tokens', 'Prize', 'Label', 'Badge',
                    'Heart Container', 'Pieces'
                ],
                "medals": [
                    'forest', 'fire', 'water', 'shadow', 'spirit', 'light'
                ],
                "dungeons": [
                    'deku', 'dodongo', 'jabu'
                ],
                "songs": [
                    "Zelda's Lullaby", "Saria's Song", "Epona's Song", "Sun's Song",
                    "Song of Time", "Song of Storms", "Minuet of Forest", "Bolero of Fire",
                    "Serenade of Water", "Requiem of Spirit", "Nocturne of Shadow",
                    "Prelude of Light"
                ]
            },
            "database": {
                "streamer": streamer,
                "channel-id": streamer.channel_id,
                "current-session": None,
                "latest-session": None
            }
        }
        for mode in self.state['modes']:
            if mode['name'] == 'songsaniyt':
                mode['items'] = self.state['guessables']['songs']
        self.commands = {
            "whitelist": ['add', 'remove', 'ban', 'unban'],
            "game_commands": {
                '!guess': partial(self._guess_command),
                '!points': partial(self._points_command),
            },
            "config_commands": {
                '!guesspoints': partial(self._guesspoints_command),
                '!firstguess': partial(self._firstguest_command),
                '!mode': partial(self._mode_command),
                '!modedel': partial(self._modedel_command)
            },
            "mod_commands": {
                '!hud': partial(self._hud_command),
                '!song': partial(self._song_command),
                '!report': partial(self._report_command)
            },
            "game_state_commands": {
                '!start': partial(self._start_command),
                '!finish': partial(self._finish_command)
            }
        }
        self.state['guessables']['dungeons'] += [
            medal for medal in self.state['guessables']['medals'] if medal != 'light']
        self.state['database']['latest-session'] = self._get_sessions()

    def _get_sessions(self):
        self.state['database']['current-session'] = Session()
        if self.state['database']['streamer'].sessions:
            return self.state['database']['streamer'].sessions[len(
                self.state['database']['streamer'].sessions) - 1]
        return None

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
            command_name = command[0]
            if command_name in self.commands['game_commands']:
                return self.commands['game_commands'][command_name](command, user)
            if (command_name in self.commands['config_commands']
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self.commands['config_commands'][command_name](command, user)
            if (command_name in self.commands['mod_commands']
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self.commands['mod_commands'][command_name](command)
            if (command_name in self.commands['game_state_commands']
                    and (permissions['whitelist'] or permissions['mod'])
                    and not permissions['blacklist']):
                return self.commands['game_state_commands'][command_name](user)
        except IndexError:
            self.logger.error('Command missing arguments')
        return None

    def _complete_guess(self, item):
        if not self.state['running']:
            self.logger.info('Guessing game not running')
            return
        if not item:
            self.logger.info('Item %s not found', item)
            return
        expiration = datetime.now() - timedelta(minutes=15)
        new_guess_deque = deque()
        first_guess = False
        for guess in self.guesses['item']:
            if guess['timestamp'] < expiration:
                continue
            if guess['guess'] is not item:
                new_guess_deque.append(guess)
                continue
            if not first_guess:
                Streamer.objects.filter( #pylint: disable=no-member
                    channel_id=self.state['database']['streamer'].channel_id,
                    participants__user_id=guess['user-id']).update(
                        inc__participants__S__session_points=
                        self.state['database']['streamer'].first_bonus,
                        inc__participants__S__total_points=
                        self.state['database']['streamer'].first_bonus)
                self.logger.info('User %s made the first correct guess earning %s extra points',
                                 guess['username'], self.state['database']['streamer'].first_bonus)
                first_guess = True
            Streamer.objects.filter( #pylint: disable=no-member
                channel_id=self.state['database']['streamer'].channel_id,
                participants__user_id=guess['user-id']).modify(
                    inc__participants__S__session_points=
                    self.state['database']['streamer'].points,
                    inc__participants__S__total_points=
                    self.state['database']['streamer'].points)
            self.logger.info('User %s guessed correctly and earned %s points',
                             guess['username'], self.state['database']['streamer'].points)
            self.guesses['item'] = new_guess_deque
            self.logger.info('Guesses completed')

    def _do_points_check(self, username):
        try:
            streamer = Streamer.objects.get( #pylint: disable=no-member
                channel_id=self.state['database']['channel-id'], participants__username=username)
            for participant in streamer.participants:
                if participant.username == username:
                    return '%s has %s points' % (username, participant.session_points)
        except Streamer.DoesNotExist: #pylint: disable=no-member
            self.logger.error('Participant with username %s does not exist in the database',
                              username)
        return None

    def _do_total_points_check(self, username):
        try:
            streamer = Streamer.objects.get( #pylint: disable=no-member
                channel_id=self.state['database']['channel-id'], participants__username=username)
            for participant in streamer.participants:
                if participant.username == username:
                    return '%s has %s points' % (username, participant.total_points)
        except Streamer.DoesNotExist: #pylint: disable=no-member
            self.logger.error('Participant with username %s does not exist in the database',
                              username)
        return None

    def _guesspoints_command(self, command):
        try:
            command_value = command[1]
            if int(command_value) > 0:
                message = 'Set points value to %s' % command_value
                self.state['database']['streamer'].points = int(command_value)
                self.state['database']['streamer'].save()
                self.logger.info(message)
                return message
            message = 'Cannot set points value lower than 0'
            self.logger.info(message)
            return message
        except ValueError:
            message = 'Cannot convert %s to an integer' % command_value
            self.logger.error(message)
            return message

    def _firstguest_command(self, command):
        try:
            command_value = command[1]
            if int(command_value) > 0:
                message = 'Set first guess bonus to %s' % command_value
                self.state['database']['streamer'].first_bonus = int(command_value)
                self.state['database']['streamer'].save()
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
        guesser = None
        try:
            streamer = Streamer.objects.get( #pylint: disable=no-member
                channel_id=self.state['database']['channel-id'],
                participants__user_id=user['user-id'])
            for participant in streamer.participants:
                if participant.user_id == int(user['user-id']):
                    guesser = participant
        except Streamer.DoesNotExist: #pylint: disable=no-member
            participant = Participant(
                username=user['username'],
                user_id=user['user-id'],
                session_points=0,
                total_points=0)
            self.state['database']['streamer'].participants.append(participant)
            self.state['database']['streamer'].save()
            self.state['database']['streamer'].reload()
            streamer = Streamer.objects.get( #pylint: disable=no-member
                channel_id=self.state['database']['channel-id'],
                participants__user_id=user['user-id'])
            for participant in streamer.participants:
                if participant.user_id == int(user['user-id']):
                    guesser = participant
            self.logger.error(
                'Participant with ID %s does not exist in the database. Creating participant.',
                user['user-id'])
        if len(command) > 2:
            subcommand_name = command[1]
            command_value = command[2:]
            if subcommand_name == 'medal':
                options = {
                    "freebie": self.state['freebie'],
                    "dungeons": self.state['guessables']['dungeons']
                }
                guess, session = guessing.do_medal_guess(
                    user, command_value, guesser, self.guesses['medal'], options)
                if guess:
                    self.guesses['medal'] = guess
                    self.state['database']['current-session'].guesses.append(session)
                return
            if subcommand_name == 'song':
                guess, session = guessing.do_song_guess(
                    user, command_value, guesser, self.guesses['song'])
                if guess:
                    self.guesses['song'] = guess
                    self.state['database']['current-session'].guesses.append(session)
                return
        if not self.state['running']:
            return
        command_value = command[1].lower()
        item = self.parse_item(command_value)
        guess, session = guessing.do_item_guess(
            user, item, guesser, self.guesses['item'])
        if guess:
            self.guesses['item'] = guess
            self.state['database']['current-session'].guesses.append(session)

    def _points_command(self, command, user):
        if len(command) == 1:
            return self._do_points_check(user['username'])
        if len(command) == 2:
            if command[1] == 'total':
                return self._do_total_points_check(user['username'])
            return self._do_points_check(command[1])
        if len(command) == 3:
            if command[2] != 'total':
                return None
            return self._do_total_points_check(command[1])
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

    def _report_command(self, command):
        if len(command) > 1:
            if command[1] == 'totals':
                self._report_totals()
                return None
        return None

    def _report_totals(self):
        amazon_s3 = boto3.resource('s3')
        filename = str(datetime.now()).replace(':', '_')
        file = os.path.join(os.path.curdir, 'reports', filename + ' totals' + '.csv')
        if not os.path.exists(file):
            try:
                os.makedirs(os.path.dirname(file))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        report_writer = csv.writer(
            open(file, 'w', newline=''))
        for participant in self.state['database']['streamer'].participants:
            report_writer.writerow([participant.user_id, participant.username,
                                    participant.total_points])
        bucket = amazon_s3.Bucket(os.environ('S3_BUCKET'))
        bucket.upload_file(file, str(datetime.now()) + '.csv', ExtraArgs={'ACL':'public-read'})

    # TODO: Fix this mess for setting the freebie medal
    def _hud_command(self, command):
        if len(command) > 1:
            subcommand_name = command[1]
            if subcommand_name in self.commands['whitelist']:
                return whitelist_commands.do_whitelist_command(
                    command,
                    self.state['database']['streamer'],
                    self.state['database']['channel-id']
                    )
            if subcommand_name in self.state['guessables']['medals']:
                return self._complete_medal_guess(command[1:])
        if not self.state['running']:
            self.logger.info('Guessing game not running')
            return None
        if len(command) > 1:
            subcommand_name = command[1]
            if subcommand_name in self.state['guessables']['medals']:
                return self._complete_medal_guess(command[1:])
        command_value = command[1].lower()
        item = self.parse_item(command_value)
        return self._complete_guess(item)

    def _song_command(self, command):
        if not self.state['running']:
            self.logger.info('Guessing game not running')
            return None
        if 'songsanity' in self.state['mode']:
            return None
        if len(command) > 1:
            return self._complete_song_guess(command[1:])
        return None

    def _complete_medal_guess(self, command):
        if len(command) < 2:
            return None
        if command[1] not in self.state['guessables']['dungeons']:
            if not self.state['running'] and command[1] == 'free':
                self.state['freebie'] = command[0]
                self.logger.info('Medal %s set to freebie', command[0])
            return None
        if command[0] in self.state['guessables']['medals']:
            if command[0] in self.state['medals']:
                self.logger.info('Medal %s already in guesses')
                if self.state['medals'][command[0]] != command[1]:
                    self.state['medals'][command[0]] = command[1]
                    self.logger.info('Medal %s set to dungeon %s', command[0], command[1])
            self.state['medals'][command[0]] = command[1]
            self.logger.info('Medal %s set to dungeon %s', command[0], command[1])
        if ((self.state['freebie'] and len(self.state['medals']) == 5)
                or len(self.state['medals']) == 6):
            local_guesses = deque()
            hiscore = 0
            for guess in self.guesses['medal']:
                count = 0
                for final in self.state['medals']:
                    if guess[final] == self.state['medals'][final]:
                        count += 1
                localguess = {
                    "user-id": guess['user-id'], "username": guess['username'], "correct": count
                    }
                local_guesses.append(localguess)
                if count > hiscore:
                    hiscore = count
            if hiscore < 1:
                return None
            for guesser in local_guesses:
                if guesser['correct'] < hiscore:
                    continue
                try:
                    streamer = Streamer.objects.get( #pylint: disable=no-member
                        channel_id=self.state['database']['channel-id'],
                        participants__user_id=guesser['user-id'])
                except Streamer.DoesNotExist: #pylint: disable=no-member
                    self.logger.error('Participant with ID %s does not exist in the database',
                                      guesser['user-id'])
                    return "User %s does not exist." % guesser['username']
                for update_participant in streamer.participants:
                    if update_participant.user_id == int(guesser['user-id']):
                        update_participant.session_points += hiscore
                        update_participant.total_points += hiscore
                self.logger.info('User %s guessed correctly and earned %s points',
                                 guesser['username'], hiscore)
                streamer.save()
                streamer.reload()
                self.guesses['medal'] = deque()
                self.logger.info('Medal guesses completed')
        return None

    def _complete_song_guess(self, command):
        if len(command) < 2:
            self.logger.info('Not enough arguments for song')
            return None
        new_song = self.parse_songs(command[0])
        new_location = self.parse_songs(command[1])
        if not new_song or not new_location:
            return None
        if new_song in self.state['guessables']['songs']:
            if new_song in self.state['songs']:
                self.logger.info('Song %s already in guesses')
                if self.state['songs'][new_song] != new_location:
                    self.state['songs'][new_song] = new_location
                    self.logger.info('Song %s set to location %s', new_song, new_location)
            self.state['songs'][new_song] = new_location
            self.logger.info('Song %s set to location %s', new_song, new_location)
        if len(self.state['songs']) == 12:
            local_guesses = deque()
            hiscore = 0
            for guess in self.guesses['song']:
                count = 0
                for final in self.state['songs']:
                    if self.parse_songs(guess[final]) == self.state['songs'][final]:
                        count += 1
                localguess = {
                    "user-id": guess['user-id'], "username": guess['username'], "correct": count
                    }
                local_guesses.append(localguess)
                if count > hiscore:
                    hiscore = count
            if hiscore < 1:
                return None
            for guesser in local_guesses:
                if guesser['correct'] < hiscore:
                    continue
                try:
                    streamer = Streamer.objects.get( #pylint: disable=no-member
                        channel_id=self.state['database']['channel-id'],
                        participants__user_id=guesser['user-id'])
                except Streamer.DoesNotExist: #pylint: disable=no-member
                    self.logger.error('Participant with ID %s does not exist in the database',
                                      guesser['user-id'])
                    return "User %s does not exist." % guesser['username']
                for update_participant in streamer.participants:
                    if update_participant.user_id == int(guesser['user-id']):
                        update_participant.session_points += hiscore
                        update_participant.total_points += hiscore
                self.logger.info('User %s guessed correctly and earned %s points',
                                 guesser['username'], hiscore)
                streamer.save()
                streamer.reload()
                self.guesses['song'] = deque()
                self.logger.info('Song guesses completed')
        return None

    def _start_command(self, user):
        if self.state['running']:
            self.logger.info('Guessing game already running')
            return None
        self.state['running'] = True
        message = 'Guessing game started by %s' % user['username']
        self.logger.info(message)
        return message

    def _finish_command(self, user):
        if not self.state['running']:
            self.logger.info('Guessing game not running')
            return None
        self.guesses['item'] = deque()
        self.guesses['medal'] = deque()
        self.guesses['song'] = deque()
        self.state['running'] = False
        self.state['freebie'] = None
        self.state['mode'].clear()
        self.state['songs'].clear()
        self.state['medals'].clear()
        self.state['database']['streamer'].sessions.append(
            self.state['database']['current-session'])
        self.state['database']['streamer'].save()
        self.state['database']['streamer'].reload()
        self.state['database']['latest-session'] = self.state['database']['current-session']
        self.state['database']['current-session'] = Session()
        for participant in self.state['database']['streamer'].participants:
            participant.session_points = 0
        self.state['database']['streamer'].save()
        self.state['database']['streamer'].reload()
        filename = str(datetime.now()).replace(':', '_')
        file = os.path.join(os.path.curdir, 'reports', filename + '.csv')
        amazon_s3 = boto3.resource('s3')
        if not os.path.exists(file):
            try:
                os.makedirs(os.path.dirname(file))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        report_writer = csv.writer(open(file, 'w', newline=''))
        for guess in self.state['database']['latest-session'].guesses:
            report_writer.writerow([guess.timestamp, guess.participant, guess.participant_name,
                                    guess.guess_type, guess.guess, guess.session_points,
                                    guess.total_points])
        bucket = amazon_s3.Bucket(os.environ['S3_BUCKET'])
        bucket.upload_file(file, str(datetime.now()) + '.csv', ExtraArgs={'ACL':'public-read'})
        message = 'Guessing game ended by %s' % user['username']
        self.logger.info(message)
        return message

    # Currently will assume !hud <item> is the Guess Completion command
    def _check_items_allowed(self, item):
        if any(skip in item for skip in self.state['guessables']['blacklist']):
            return False
        for modes in self.state['modes']:
            if modes['name'] not in self.state['mode'] and item in modes['items']:
                return False
        return True

    # Integrate with the database in the future
    def parse_songs(self, songcode):
        """Searches for a song with the value of songcode in its codes entry."""
        for item in self.items:
            if 'name' in item:
                if not item['name'] in self.state['guessables']['songs']:
                    continue
            if 'stages' in item:
                codes = []
                for stage in item['stages']:
                    if 'codes' in stage:
                        if any(code in stage['codes'].split(',') for code in codes):
                            continue
                        for code in stage['codes'].split(','):
                            codes += [code.strip()]
                if songcode in codes:
                    return item['name']
        return None

    def parse_item(self, guess):
        """Searches for a item with the value of guess in its codes entry."""
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
