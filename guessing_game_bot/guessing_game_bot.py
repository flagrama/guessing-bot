"""This module provides an interface for running a guessing game."""
import os.path
import errno
from datetime import datetime
from collections import deque
from functools import partial
import csv

import boto3
import jstyleson

from .database import DbStreamer, Session, Participant
from .mode import Mode
from .game import GuessingGame
from . import guessing
from . import whitelist_commands
from .guessable import Guessable
from .access_list import AccessList
from . import settings

class GuessingGameBot():
    """This is a class for running a guessing game."""
    def __init__(self, streamer):
        """The constructor for GuessingGame class."""
        self.__name = streamer.name
        self.__channel_id = streamer.channel_id
        self.__access_list = AccessList(
            self.__channel_id, streamer.whitelist, streamer.blacklist)
        self.__participants = streamer.participants
        self.logger = settings.init_logger(__name__)
        self.__guessing_game = GuessingGame(
            streamer.guessables,
            [], #streamer.modes,
            streamer.multi_guess
        )

# TODO: Grab from database instead of hardcoding
        # self.state['modes'] += [Mode('keysanity', 'Boss Key')]
        # self.state['modes'] += [Mode('egg', 'Child Trade')]
        # self.state['modes'] += [Mode('ocarina', 'Ocarina')]
        # self.__guessing_game = GuessingGame(
        #     self.guessables,
        #     self.state['modes'].modes,
        #     self.state['guessables']
        # )
# End Region
        self.commands = {
            "whitelist": ['add', 'remove', 'ban', 'unban'],
            "game_commands": {
                '!guess': partial(self.guess_command),
                '!points': partial(self.points_command),
            },
            "config_commands": {
                '!guesspoints': partial(self._guesspoints_command),
                '!firstguess': partial(self._firstguest_command),
                '!mode': partial(self._mode_command),
                '!modedel': partial(self._modedel_command)
            },
            "mod_commands": {
                '!hud': partial(self._hud_command),
                '!report': partial(self._report_command)
            },
            "game_state_commands": {
                '!start': partial(self._start_command),
                '!finish': partial(self._finish_command)
            }
        }
        #self.state['database']['latest-session'] = self._get_sessions()

    def _get_sessions(self):
        self.state['database']['current-session'] = Session()
        if self.state['database']['streamer'].sessions:
            return self.state['database']['streamer'].sessions[len(
                self.state['database']['streamer'].sessions) - 1]
        return None

    def do_command(self, user, is_mod, command_name, command):
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
            if command_name in self.commands['game_commands']:
                return self.commands['game_commands'][command_name](self, command, user)
            if (command_name in self.commands['config_commands']
                    and is_mod or self.__access_list.user_in_whitelist(user['user_id'])
                    and not self.__access_list.user_in_blacklist(user['user_id'])):
                return self.commands['config_commands'][command_name](command, user)
            if (command_name in self.commands['mod_commands']
                    and is_mod or self.__access_list.user_in_whitelist(user['user_id'])
                    and not self.__access_list.user_in_blacklist(user['user_id'])):
                return self.commands['mod_commands'][command_name](command)
            if (command_name in self.commands['game_state_commands']
                    and is_mod or self.__access_list.user_in_whitelist(user['user_id'])
                    and not self.__access_list.user_in_blacklist(user['user_id'])):
                return self.commands['game_state_commands'][command_name](user)
        except IndexError:
            self.logger.error('Command missing arguments')
        return None

    def _do_whitelist_command(self, command, username):
        """Calls the command function the user invokes."""
        logger = settings.init_logger(__name__)
        commands = {
            "add": partial(self.__access_list.add_user_to_whitelist),
            "remove": partial(self.__access_list.remove_user_from_whitelist),
            "ban": partial(self.__access_list.add_user_to_blacklist),
            "unban": partial(self.__access_list.remove_user_from_blacklist)
        }
        try:
            if command in commands:
                return commands[command](username)
        except IndexError:
            logger.error('Command missing arguments')
            return None
        except KeyError:
            logger.error('Command missing')
            return None
        return None

    def _start_command(self, user):
        if self.state['running']:
            self.logger.info('Guessing game already running')
            return None
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'items.json')
        with open(path) as items:
            self.guessables.items = (jstyleson.load(items), self.state['mode'])
        self.state['running'] = True
        message = 'Guessing game started by %s' % user['username']
        self.logger.info(message)
        return message

    def _finish_command(self, user):
        if not self.state['running']:
            self.logger.info('Guessing game not running')
            return None
        print(self.guesses)
        for queues in self.guesses:
            self.guesses[queues] = deque()
        print(self.guesses)
        self.state['running'] = False
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
        if os.environ['AWS_ACCESS_KEY_ID']:
            amazon_s3 = boto3.resource('s3')
            bucket = amazon_s3.Bucket(os.environ['S3_BUCKET'])
            bucket.upload_file(file, str(datetime.now()) + '.csv', ExtraArgs={'ACL':'public-read'})
        message = 'Guessing game ended by %s' % user['username']
        self.logger.info(message)
        return message

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

    def guess_command(self, guessing_game, command, user):
        guesser = None
        for participant in guessing_game.state['database']['streamer'].participants:
            if participant.user_id == int(user['user-id']):
                guesser = participant
        if guesser is None:
            guessing_game.state['database']['streamer'].reload()
            participant = Participant(
                username=user['username'],
                user_id=user['user-id'],
                session_points=0,
                total_points=0)
            guessing_game.state['database']['streamer'].participants.append(participant)
            guessing_game.state['database']['streamer'].save()
            for participant in guessing_game.state['streamer'].participants:
                if participant.user_id == int(user['user-id']):
                    guesser = participant
            guessing_game.logger.info(
                'Participant with ID %s does not exist in the database. Creating participant.',
                user['user-id'])
        if len(command) > 2 and not guessing_game.state['running']:
            subcommand_name = command[1]
            command_value = command[2:]
            self.logger.debug('Item type: %s, Location value: %s', subcommand_name, command_value)
            if subcommand_name in self.guessables.extra_item_types:
                guessing.do_extra_guess(user, command_value, subcommand_name,
                                        guesser, guessing_game)
        if not guessing_game.state['running']:
            return
        command_value = command[1].lower()
        item = self.guessables.get_item(command_value)
        if not item:
            self.logger.info('Item %s not found', command_value)
        guessing.do_item_guess(user, item, guesser, guessing_game)

    @staticmethod
    def points_command(guessing_game, command, user):
        if len(command) == 1:
            return guessing_game.points_check(user['username'])
        if len(command) == 2:
            if command[1] == 'total':
                return guessing_game.total_points_check(user['username'])
            return guessing_game.points_check(command[1])
        if len(command) == 3:
            if command[2] != 'total':
                return None
            return guessing_game.total_points_check(command[1])
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
            if mode == modes.name and mode not in self.state['mode']:
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

    def _hud_command(self, command):
        if len(command) > 0:
            subcommand_name = command[0]
            if subcommand_name in self.commands['whitelist']:
                return self._do_whitelist_command(subcommand_name, command[1])
            if subcommand_name in self.guessables.extra_item_types:
                return guessing.complete_extra_guess(self, command[0:])
        if not self.state['running']:
            self.logger.info('Guessing game not running')
            return None
        command_value = command[0].lower()
        item = self.guessables.get_item(command_value)
        if not item:
            self.logger.info('Item %s not found', command_value)
        return guessing.complete_guess(self, item)

    def points_check(self, username):
        try:
            streamer = DbStreamer.objects.get( #pylint: disable=no-member
                channel_id=self.state['database']['channel-id'], participants__username=username)
            for participant in streamer.participants:
                if participant.username == username:
                    return '%s has %s points' % (username, participant.session_points)
        except DbStreamer.DoesNotExist: #pylint: disable=no-member
            self.logger.error('Participant with username %s does not exist in the database',
                              username)
        return None

    def total_points_check(self, username):
        try:
            streamer = DbStreamer.objects.get( #pylint: disable=no-member
                channel_id=self.state['database']['channel-id'], participants__username=username)
            for participant in streamer.participants:
                if participant.username == username:
                    return '%s has %s points' % (username, participant.total_points)
        except DbStreamer.DoesNotExist: #pylint: disable=no-member
            self.logger.error('Participant with username %s does not exist in the database',
                              username)
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

    # Currently will assume !hud <item> is the Guess Completion command
