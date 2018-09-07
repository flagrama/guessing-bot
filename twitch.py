"""Stores Twitch API calls."""
import os
import requests

import settings

CLIENT_ID = os.environ['TWITCH_ID']
TOKEN = os.environ['TWITCH_TOKEN']

def get_user_id(username):
    """Gets the user ID of a user from their username."""
    logger = settings.init_logger(__name__)
    url = 'https://api.twitch.tv/helix/users?login=%s' % username
    headers = {'Client-ID': CLIENT_ID}
    request = requests.get(url, headers=headers).json()

    try:
        user_id = request['data'][0]['id']
    except IndexError:
        logger.error('User not found by Twitch API')
        return None
    logger.debug('Found user ID %s', user_id)
    return user_id
