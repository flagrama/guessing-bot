"""The module that starts the IRC chat bot."""
import argparse
import logging

import settings
import bot

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def main():
    """The Main function of the bot. Starts the IRC bot."""
    parser = argparse.ArgumentParser(
        description='A bot for making a game of guessing upcoming items in randomizers.')
    parser.add_argument('--debug', dest='debug', action='store_true', default=False)
    args = parser.parse_args()
    settings.DEBUG = args.debug
    try:
        client = bot.TwitchBot()
        client.start()
    except KeyboardInterrupt:
        print('\n')
        LOGGER.info('SIGINT recieved. Terminating.')

if __name__ == "__main__":
    main()
