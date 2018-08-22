import sys
import os
import logging

import irc.bot
import requests
import mongoengine as mongodb

from database.streamer import *
import customCommands
import defaultCommands

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
        self.commands = ['!addcom', '!delcom', '!editcom']
        self.logger.debug(self.commands)

    def get_channel_id(self):
        url = 'https://api.twitch.tv/helix/users?login=%s' % self.channel_name
        headers = {'Client-ID': self.client_id}
        r = requests.get(url, headers=headers).json()

        self.channel_id = r['data'][0]['id']
        self.logger.debug('Channel ID is %s' % self.channel_id)

    def get_self_id(self):
        url = 'https://api.twitch.tv/helix/users?login=%s' % self.username
        headers = {'Client-ID': self.client_id}
        r = requests.get(url, headers=headers).json()

        self.id = r['data'][0]['id']
        self.logger.debug('Self ID is %s' % self.id)

    def irc_connect(self):
        server = 'irc.chat.twitch.tv'
        port = 6667
        self.logger.info('Connecting to %s on port %s...' % (server, port))
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, self.token)], self.username, self.username)
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
        for streamer in Streamer.objects(channel_id=self.channel_id):
            self.streamer = streamer

        if not hasattr(self, 'streamer'):
            self.logger.debug('Unable to find streamer with ID %s in the database' % self.channel_id)
            self.logger.debug('Creating new entry for streamer with ID %s' % self.channel_id)
            self.streamer = Streamer(name = self.channel_name, channel_id = self.channel_id)
            self.streamer.save()

        for command in self.streamer.commands:
            self.commands += [command.name]
            self.logger.debug(self.commands)

    def do_command(self, event, command):
        connection = self.connection

        if command[0] in self.default_commands:
            defaultCommands.do_default_command(self, connection, command)
        else:
            self.logger.debug('Built-in command not found')
            for custom_command in self.streamer.commands:
                if custom_command.name == command[0]:
                    self.logger.info('Custom command %s received' % custom_command.name)
                    connection.privmsg(self.channel, custom_command.output)

    

    # Events
    def on_welcome(self, connection, event):
        self.logger.info('Joining %s' % self.channel)
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

