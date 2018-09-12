"""Holds Twitch API class."""
import requests

from . import settings

class TwitchAPI():
    """A class for interacting with the Twitch API."""
    def __init__(self, client_id):
        self.logger = settings.init_logger(__name__)
        self.client_id = client_id
        self.logger.debug('Twitch Client ID: %s', self.client_id)

    def get_user_id(self, username):
        """Gets the user ID of a user from their username."""
        url = 'https://api.twitch.tv/helix/users?login=%s' % username.lower()
        self.logger.debug('Getting User ID for user %s', username)
        headers = {'Client-ID': self.client_id}
        request = requests.get(url, headers=headers).json()
        self.logger.debug('GET %s', url)

        try:
            user_id = request['data'][0]['id']
            self.logger.debug('User ID: %s', user_id)
        except IndexError:
            self.logger.error('User not found by Twitch API')
            return None
        self.logger.debug('Found %s ID %s', username, user_id)
        return user_id
