"""This module provides an interface for running a guessing game."""
from functools import partial
from .database import Participant
from .game import GuessingGame
from .access_list import AccessList
from . import settings

class GuessingGameBot():
    """This is a class for running a guessing game."""
    def __init__(self, streamer):
        self.__logger = settings.init_logger(__name__)
        self.__streamer = streamer
        self.__access_list = AccessList(
            self.__streamer.channel_id, streamer.whitelist, streamer.blacklist)
        self.__guessing_game = GuessingGame(
            streamer.modes,
            streamer.multi_guess)

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
                '!report': partial(self._report_command)
            },
            "game_state_commands": {
                '!start': partial(self._start_command),
                '!finish': partial(self._finish_command)
            }
        }

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
            is_whitelist = False
            if not is_mod:
                is_whitelist = self.__access_list.user_in_whitelist(user['user_id'])
            is_blacklist = self.__access_list.user_in_blacklist(user['user_id'])
            if command_name in self.commands['game_commands']:
                print(command_name)
                return self._do_game_command(command_name, user, command)
            if (command_name in self.commands['config_commands']
                    and is_mod or is_whitelist and not is_blacklist):
                return self.commands['config_commands'][command_name](command, user)
            if (command_name in self.commands['mod_commands']
                    and is_mod or is_whitelist and not is_blacklist):
                return self.commands['mod_commands'][command_name](command)
            if (command_name in self.commands['game_state_commands']
                    and is_mod or is_whitelist and not is_blacklist):
                return self.commands['game_state_commands'][command_name](user)
        except IndexError:
            self.__logger.error('Command missing arguments')
        return None

    def _do_game_command(self, action, user, command):
        return self.commands['game_commands'][action](user, command)

    def _do_whitelist_command(self, command, username):
        """Calls the command function the user invokes."""
        logger = settings.init_logger(__name__)
        if len(command) < 2:
            return None
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
        self.__streamer.reload()
        items = self.__streamer.guessables
        return self.__guessing_game.start_guessing_game(user, items)

    def _finish_command(self, user):
        message = self.__guessing_game.end_guessing_game(user)
        for participant in self.__streamer.participants:
            participant.session_points = 0
        self.__streamer.participants = self.__streamer.participants
        self.__streamer.save()
        return message

    def _guesspoints_command(self, command, user):
        points_value = command[0]
        try:
            if int(points_value) >= 0:
                message = '%s set points value to %s' % (user['username'], points_value)
                self.__streamer.points = int(points_value)
                self.__streamer.save()
                self.__logger.info(message)
                return message
            message = 'Cannot set points value lower than 0'
            self.__logger.info(message)
            return message
        except ValueError:
            message = 'Cannot convert %s to an integer' % points_value
            self.__logger.error(message)
            return message

    def _firstguest_command(self, command, user):
        points_value = command[0]
        try:
            if int(points_value) >= 0:
                message = '%s set first guess bonus value to %s' % (user['username'], points_value)
                self.__streamer.first_bonus = int(points_value)
                self.__streamer.save()
                self.__logger.info(message)
                return message
            message = 'Cannot set first guess bonus lower than 0'
            self.__logger.info(message)
            return message
        except ValueError:
            message = 'Cannot convert %s to an integer' % points_value
            self.__logger.error(message)
            return message

    def _guess_command(self, user, command):
        guesser = None
        for participant in self.__streamer.participants:
            if participant.user_id == user['user_id']:
                guesser = participant
        if guesser is None:
            self.__logger.info(
                'Participant %s does not exist in the database. Creating participant.',
                user['user_id'])
            self.__streamer.reload()
            participant = Participant(
                username=user['username'],
                user_id=user['user_id'],
                session_points=0,
                total_points=0)
            self.__streamer.participants.append(participant)
            self.__streamer.participants = self.__streamer.participants
            self.__streamer.save()
            for participant in self.__streamer.participants:
                if participant.user_id == user['user_id']:
                    guesser = participant
        self.__guessing_game.guess(guesser, command)

    def _points_command(self, user, command):
        if not command:
            return self.__points_check(user['username'])
        if len(command) == 1:
            if command[0] == 'total':
                return self.__total_points_check(user['username'])
            return self.__points_check(command[0])
        if len(command) == 2:
            if command[1] != 'total':
                return None
            return self.__total_points_check(command[0])
        return None

    def _mode_command(self, command, user):
        mode = command[0]
        message = None
        if not command:
            message = 'Mode command requires a mode argument'
            self.__logger.info(message)
        if mode == 'normal':
            command_message = self.__guessing_game.reset_modes(user)
        else:
            command_message = self.__guessing_game.add_mode(mode, user)
        if command_message:
            return command_message
        if message:
            return message
        return None

    def _modedel_command(self, command, user):
        mode = command[0]
        message = None
        if not command:
            message = 'Mode Delete command requires a mode argument'
            self.__logger.info(message)
        command_message = self.__guessing_game.remove_mode(mode, user)
        if command_message:
            return command_message
        if message:
            return message
        return None

    def _report_command(self, command):
        if len(command) > 1:
            if command[1] == 'totals':
                self.__guessing_game.report_totals(self.__streamer.participants)
                return None
        return None

    def _hud_command(self, command):
        if command:
            subcommand_name = command[0]
            if subcommand_name in self.commands['whitelist']:
                return self._do_whitelist_command(subcommand_name, command[1])
        return self.__guessing_game.complete_guess(self.__streamer, command)

    def __points_check(self, username):
        for participant in self.__streamer.participants:
            if participant.username == username:
                return '%s has %s points' % (username, participant.session_points)
        self.__logger.info('Participant with username %s does not exist in the database', username)
        return None

    def __total_points_check(self, username):
        for participant in self.__streamer.participants:
            if participant.username == username:
                return '%s has %s points' % (username, participant.total_points)
        self.__logger.error('Participant with username %s does not exist in the database', username)
        return None
