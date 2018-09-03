import os
import logging
import requests

LOGGER = logging.getLogger(__name__)
CLIENT_ID = os.environ['TWITCH_ID']
TOKEN = os.environ['TWITCH_TOKEN']

def get_user_id(username):
    url = 'https://api.twitch.tv/helix/users?login=%s' % username
    headers = {'Client-ID': CLIENT_ID}
    r = requests.get(url, headers=headers).json()

    try:
        user_id = r['data'][0]['id']
    except IndexError:
        LOGGER.error('User not found by Twitch API')
        return None
    LOGGER.debug('Found user ID %s', user_id)
    return user_id
