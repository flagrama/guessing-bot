import sys
import os
import logging

import irc.bot
import requests
import mongoengine as mongodb

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, debug):
        self.init_logging(debug)

        self.client_id = os.environ['TWITCH_ID']
        self.token = os.environ['TWITCH_TOKEN']
        username = os.environ['TWITCH_BOT_NAME']
        self.channel_name = os.environ['TWITCH_CHANNEL']
        self.channel = '#%s' % self.channel_name

        self.get_channel_id
        self.irc_connect(username)
        self.database_connect()

    # Methods
    def init_logging(self, debug):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def irc_connect(self, username):
        server = 'irc.chat.twitch.tv'
        port = 6667
        self.logger.info('Connecting to %s on port %s...' % (server, port))
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, self.token)], username, username)
        self.logger.info('Connecting to database...')

    def get_channel_id(self):
        url = 'https://api.twitch.tv/helix/users?login=%s' % self.channel_name
        headers = {'Client-ID': self.client_id}
        r = requests.get(url, headers=headers).json()

        self.channel_id = r['data'][0]['id']

    def database_connect(self):
        try:
            mongodb_uri = os.environ['MONGODB_URI']
            mongodb.connect(host=mongodb_uri)
            self.logger.info('Connected to database.')
        except mongodb.connection.MongoEngineConnectionError as e:
            self.logger.error('Unable to connect to database!')
            self.logger.error(e)
            raise e

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
