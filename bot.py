import sys
import os
import logging

import irc.bot
import requests
import mongoengine as mongodb

from database.streamer import Streamer
import customCommands
import defaultCommands
import whitelistCommands
import guessing_game

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, debug):
        self.init_logging(debug)

        self.client_id = os.environ['TWITCH_ID']
        self.token = os.environ['TWITCH_TOKEN']
        self.username = os.environ['TWITCH_BOT_NAME']
        self.channel_name = os.environ['TWITCH_CHANNEL']
        self.channel = '#%s' % self.channel_name

        self.get_default_commands()
        self.get_channel_id()
        self.get_self_id()
        self.irc_connect()
        self.database_connect()
        self.get_streamer_from_database()
        self.guessing_game = guessing_game.GuessingGame(self.streamer)
        self.commands += self.guessing_game.commands

    # Methods
    def init_logging(self, debug):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def get_default_commands(self):
        self.default_commands = ['!addcom', '!delcom', '!editcom', '!hud']
        self.whitelist_commands = [
            '!hud add', '!hud remove', '!hud ban', '!hud unban'
            ]
        self.commands = self.default_commands
        self.logger.debug(self.commands)

    def get_user_id(self, username):
        url = 'https://api.twitch.tv/helix/users?login=%s' % username
        headers = {'Client-ID': self.client_id}
        r = requests.get(url, headers=headers).json()

        try:
            user_id = r['data'][0]['id']
        except IndexError:
            self.logger.error('User not found by Twitch API')
            return None
        self.logger.debug('Found user ID %s', user_id)
        return user_id

    def get_channel_id(self):
        self.channel_id = self.get_user_id(self.channel_name)
        self.logger.debug('Channel ID is %s', self.channel_id)

    def get_self_id(self):
        self.id = self.get_user_id(self.username)
        self.logger.debug('Self ID is %s', self.id)

    def irc_connect(self):
        server = 'irc.chat.twitch.tv'
        port = 6667
        self.logger.info('Connecting to %s on port %s...', server, port)
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port, self.token)], self.username, self.username)
        self.logger.info('Connecting to database...')

    def database_connect(self):
        try:
            mongodb_uri = os.environ['MONGODB_URI']
            mongodb.connect(host=mongodb_uri)
            self.logger.debug('Connected to database.')
        except mongodb.connection.MongoEngineConnectionError as e:
            self.logger.error('Unable to connect to database!')
            self.logger.error(e)
            raise e

    def get_streamer_from_database(self):
        for streamer in Streamer.objects(channel_id=self.channel_id): #pylint: disable=no-member
            self.streamer = streamer

        if not hasattr(self, 'streamer'):
            self.logger.debug(
                'Unable to find streamer with ID %s in the database', self.channel_id)
            self.logger.debug('Creating new entry for streamer with ID %s', self.channel_id)
            self.streamer = Streamer(name = self.channel_name, channel_id = self.channel_id)
            self.streamer.save()

        for command in self.streamer.commands:
            self.commands += [command.name]
        self.logger.debug(self.commands)

    def get_user_permissions(self, event):
        mod = False
        whitelist = False
        blacklist = False

        user_string = event.source.split('!')
        for tag in event.tags:
            if tag['key'] == 'user-id':
                if tag['value'] == self.channel_id:
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
            "user-id": self.get_user_id(user_string[0]),
            "channel-id": self.channel_id
        }
        return user, permissions

    def do_command(self, event, command):
        connection = self.connection
        command_name = command[0]
        user, permissions = self.get_user_permissions(event)

        if len(command) > 1:
            sub_command = command[1]
            if (' '.join([command_name, sub_command]) in self.whitelist_commands
                    and user['user-id'] == self.streamer.channel_id):
                whitelistCommands.do_whitelist_command(self, connection, command)
                return
        if command_name in self.guessing_game.commands:
            message = self.guessing_game.do_command(user, permissions, command)
            if message:
                self.connection.privmsg(self.channel, message)
            return
        if command_name in self.default_commands and permissions['mod']:
            defaultCommands.do_default_command(self, connection, command)
            return
        self.logger.debug('Built-in command not found')
        try:
            streamer = Streamer.objects.get( #pylint: disable=no-member
                channel_id = self.streamer.channel_id, commands__name = command_name)
            for custom_command in streamer.commands:
                self.logger.info('Custom command %s received', custom_command.name)
                connection.privmsg(self.channel, custom_command.output)
        except Streamer.DoesNotExist: #pylint: disable=no-member
            self.logger.error(
                'Custom command %s not found in database but is in command list', command_name)

    # Events
    def on_welcome(self, connection, event):
        self.logger.info('Joining %s', self.channel)
        self.logger.debug(event)

        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        self.logger.debug(event)
        for tag in event.tags:
            if tag['key'] == 'user-id':
                if tag['value'] == self.id:
                    self.logger.info('Ignoring message from self')
                    return
        command = event.arguments[0].split(' ')
        if command[0] in self.commands:
            self.do_command(event, command)

