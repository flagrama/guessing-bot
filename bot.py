import sys
import os
import logging

import irc.bot
import requests

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        logging.basicConfig()
        self.logger = logging.getLogger('TwitchBot')
        self.logger.setLevel(logging.INFO)

        self.client_id = os.environ['TWITCH_ID']
        self.token = os.environ['TWITCH_TOKEN']
        username = os.environ['TWITCH_BOT_NAME']
        channel = os.environ['TWITCH_CHANNEL']
        self.channel = '#%s' % channel

        url = 'https://api.twitch.tv/helix/users?login=%s' % channel
        headers = {'Client-ID': self.client_id}
        r = requests.get(url, headers=headers).json()

        self.channel_id = r['data'][0]['id']

        server = 'irc.chat.twitch.tv'
        port = 6667
        self.logger.info('Connecting to %s on port %s...' % (server, port))
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, self.token)], username, username)
    
    def on_welcome(self, c, e):
        self.logger.info('Joining %s' % self.channel)

        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
