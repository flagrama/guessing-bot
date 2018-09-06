import os
import logging

import irc.bot
import mongoengine

from database import Streamer
import settings
import twitch
import default_commands
import guessing_game

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        if settings.DEBUG:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.config = {
            "username": os.environ['TWITCH_BOT_NAME'],
            "channel_name": os.environ['TWITCH_CHANNEL'],
            "channel": '#%s' % os.environ['TWITCH_CHANNEL']
        }
        self.commands = {
            "default": ['!addcom', '!delcom', '!editcom'],
            "guessing-game": [],
            "custom": []
        }
        self.get_channel_id()
        self.get_self_id()
        server = 'irc.chat.twitch.tv'
        port = 6667
        self.logger.info('Connecting to %s on port %s...', server, port)
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port, twitch.TOKEN)], self.config['username'], self.config['username'])
        self.logger.info('Connecting to database...')
        self.database_connect()
        self.get_streamer_from_database()
        self.guessing_game = guessing_game.GuessingGame(self.streamer)
        self.commands['guessing-game'] = self.guessing_game.commands['default']
        self.logger.debug(self.commands)

    # Methods
    def init_logging(self, debug):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def get_default_commands(self):
        self.default_commands = ['!addcom', '!delcom', '!editcom']
        self.commands = self.default_commands[:]
        self.logger.debug(self.commands)

    def get_channel_id(self):
        self.config['channel_id'] = twitch.get_user_id(self.config['channel_name'])
        self.logger.debug('Channel ID is %s', self.config['channel_id'])

    def get_self_id(self):
        self.config['id'] = twitch.get_user_id(self.config['username'])
        self.logger.debug('Self ID is %s', self.config['id'])


    def database_connect(self):
        try:
            mongodb_uri = os.environ['MONGODB_URI']
            mongoengine.connect(host=mongodb_uri)
            self.logger.debug('Connected to database.')
        except mongoengine.connection.MongoEngineConnectionError as e:
            self.logger.error('Unable to connect to database!')
            self.logger.error(e)
            raise e

    def get_streamer_from_database(self):
        for streamer in Streamer.objects(channel_id=self.config['channel_id']): #pylint: disable=no-member
            self.streamer = streamer

        if not hasattr(self, 'streamer'):
            self.logger.debug(
                'Unable to find streamer with ID %s in the database', self.config['channel_id'])
            self.logger.debug('Creating new entry for streamer with ID %s', self.config['channel_id'])
            self.streamer = Streamer(name = self.config['channel_name'], channel_id = self.config['channel_id'])
            self.streamer.save()

        for command in self.streamer.commands:
            self.commands['custom'] += [command.name]

    def get_user_permissions(self, event):
        mod = False
        whitelist = False
        blacklist = False

        user_string = event.source.split('!')
        for tag in event.tags:
            if tag['key'] == 'user-id':
                if tag['value'] == self.config['channel_id']:
                    mod = True
                if Streamer.objects.filter( #pylint: disable=no-member
                        channel_id=self.streamer.channel_id,
                        whitelist__user_id=tag['value']):
                    whitelist = True
                if Streamer.objects.filter( #pylint: disable=no-member
                        channel_id=self.streamer.channel_id,
                        blacklist__user_id=tag['value']):
                    blacklist = True
            if tag['key'] == 'mod':
                if tag['value'] == 1:
                    mod = True
        permissions = {
            "mod": mod,
            "whitelist": whitelist,
            "blacklist": blacklist
        }
        user = {
            "username": user_string[0],
            "user-id": twitch.get_user_id(user_string[0]),
            "channel-id": self.config['channel_id']
        }
        return user, permissions

    def do_command(self, event, command):
        connection = self.connection
        command_name = command[0].lower()
        user, permissions = self.get_user_permissions(event)
        if command_name in self.commands['guessing-game']:
            message = self.guessing_game.do_command(user, permissions, command)
            if message:
                self.connection.privmsg(self.config['channel'], message)
            return
        if command_name in self.commands['default'] and permissions['mod']:
            message = default_commands.do_default_command(self, command)
            if message:
                self.connection.privmsg(self.config['channel'], message)
            return
        self.logger.debug('Built-in command not found')
        try:
            streamer = Streamer.objects.get( #pylint: disable=no-member
                channel_id = self.streamer.channel_id, commands__name = command_name)
            for custom_command in streamer.commands:
                if command_name in custom_command['name']:
                    self.logger.info('Custom command %s received', custom_command.name)
                    connection.privmsg(self.config['channel'], custom_command.output)
        except Streamer.DoesNotExist: #pylint: disable=no-member
            self.logger.error(
                'Custom command %s not found in database but is in command list', command_name)

    # Events
    def on_welcome(self, connection, event):
        self.logger.info('Joining %s', self.config['channel'])
        self.logger.debug(event)

        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')
        connection.join(self.config['channel'])

    def on_pubmsg(self, connection, event):
        self.logger.debug(event)
        for tag in event.tags:
            if tag['key'] == 'user-id':
                if tag['value'] == self.config['id']:
                    self.logger.info('Ignoring message from self')
                    return
        command = event.arguments[0].split(' ')
        commands = []
        for existing in self.commands:
            commands += self.commands[existing]
        if command[0].lower() in commands:
            self.do_command(event, command)
