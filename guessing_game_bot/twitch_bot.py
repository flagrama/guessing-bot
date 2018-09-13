"""A Twitch chat IRC bot."""
import os

import irc.bot
import mongoengine

from .database import DbStreamer
from .twitch import TwitchAPI
from . import default_commands
from .guessing_game_bot import GuessingGameBot
from . import settings

SERVER = 'irc.chat.twitch.tv'
PORT = 6667

class TwitchBot(irc.bot.SingleServerIRCBot):
    """An IRC bot for connecting to Twitch chat servers."""
    def __init__(self):
        self.logger = settings.init_logger(__name__)
        self.twitch = TwitchAPI(os.environ['TWITCH_ID'])
        self.logger.info('Twitch API calls initialized.')
        self.data = {
            "streamers": {},
            "guessing_game_bots": {},
            "users": {}
        }
        self.config = {
            "username": os.environ['TWITCH_BOT_NAME']
        }
        self.commands = {
            "default": ['!addcom', '!delcom', '!editcom'],
            "guessing-game": []
        }
        self._get_self_id()
        self._database_connect()
        for streamer in DbStreamer.objects: #pylint: disable=no-member
            self.data['streamers'][streamer.channel_id] = streamer
            self.commands[streamer.channel_id] = []
            for command in streamer.commands:
                self.commands[streamer.channel_id] += [command.name]
        self.logger.info('Connecting to %s on port %s...', SERVER, PORT)
        irc.bot.SingleServerIRCBot.__init__(
            self, [(SERVER, PORT, os.environ['TWITCH_TOKEN'])],
            self.config['username'], self.config['username'])
        self.logger.info('Connecting to database...')
        for channel_id, streamer in self.data['streamers'].items():
            self.data['guessing_game_bots'][channel_id] = GuessingGameBot(streamer)
            if not self.commands['guessing-game']:
                self.logger.info('Retrieving GuessingGame commands.')
                current_bot = self.data['guessing_game_bots'][channel_id]
                for command_category in current_bot.commands:
                    current_commands = current_bot.commands
                    for command in current_commands[command_category]:
                        self.commands['guessing-game'] += [command]
        self.logger.debug(self.commands)

    def _get_self_id(self):
        self.config['id'] = self.twitch.get_user_id(self.config['username'])
        self.logger.debug('Bot ID is %s', self.config['id'])

    def _database_connect(self):
        try:
            mongodb_uri = os.environ['MONGODB_URI']
            mongoengine.connect(host=mongodb_uri)
            self.logger.debug('Connected to database.')
        except mongoengine.connection.MongoEngineConnectionError as error:
            self.logger.error('Unable to connect to database!')
            self.logger.error(error)
            raise error

    def _get_user(self, event):
        user_hash = event.target+event.source
        if user_hash in self.data['users']:
            return self.data['users'][user_hash]
        for tag in event.tags:
            if tag['key'] == 'display-name':
                username = tag['value']
            if tag['key'] == 'room-id':
                room_id = tag['value']
            if tag['key'] == 'user-id':
                user_id = tag['value']
        self.data['users'][user_hash] = {
            "username": username,
            "room_id": room_id,
            "room_name": event.target,
            "user_id": int(user_id)
        }
        if room_id == user_id:
            self.data['users'][user_hash]['is_streamer'] = True
        return self.data['users'][user_hash]

    def _is_user_mod(self, event):
        for tag in event.tags:
            if tag['key'] == 'mod':
                if tag['value'] == '1':
                    return True
        return False

    def _do_command(self, event, connection, command_name, value):
        user = self._get_user(event)
        if 'is_streamer' in user:
            is_mod = True
        else:
            is_mod = self._is_user_mod(event)
        if command_name in self.commands['guessing-game']:
            if user['room_id'] in self.data['guessing_game_bots']:
                current_bot = self.data['guessing_game_bots'][user['room_id']]
            if not current_bot:
                return
            message = current_bot.do_command(user, is_mod, command_name, value)
            if message:
                connection.privmsg(user['room_name'], message)
            return
        if command_name in self.commands['default'] and is_mod:
            message = default_commands.do_default_command(self, value)
            if message:
                connection.privmsg(user['room_name'], message)
            return
        self.logger.debug('Built-in command not found')
        for custom_command in self.data['streamers'][user['room_id']].commands:
            if command_name in custom_command['name']:
                self.logger.info('Custom command %s receieved', custom_command.name)
                connection.privmsg(user['room_name'], custom_command.output)
                return
        self.logger.error('Custom command %s not found in database but is in command list',
                          command_name)

    # Events
    def on_welcome(self, connection, event):
        """Event that executes when IRC bot is welcomed to the IRC server."""
        self.logger.debug(event)
        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')
        for streamer in self.data['streamers'].values():
            channel = '#%s' % streamer.name
            connection.join(channel)
            self.logger.info('Joined %s', channel)

    def on_pubmsg(self, connection, event):
        """Event that executes whenever an IRC message is receieved."""
        self.logger.debug('Message recieved: %s', event)
        for tag in event.tags:
            if tag['key'] == 'user-id':
                if tag['value'] == self.config['id']:
                    self.logger.info('Ignoring message from self')
                    return
        command = event.arguments[0].split(' ')
        commands = []
        for existing in self.commands.values():
            commands += existing
        if command[0].lower() in commands:
            self._do_command(event, connection, command[0], command[1:])
