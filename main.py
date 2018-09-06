"""The module that starts the IRC chat bot."""
import argparse

import settings
import bot

def main():
    """The Main function of the bot. Starts the IRC bot."""
    parser = argparse.ArgumentParser(
        description='A bot for making a game of guessing upcoming items in randomizers.')
    parser.add_argument('--debug', dest='debug', action='store_true', default=False)
    args = parser.parse_args()
    settings.DEBUG = args.debug
    logger = settings.init_logger(__name__)
    try:
        client = bot.TwitchBot()
        client.start()
    except KeyboardInterrupt:
        print('\n')
        logger.info('SIGINT recieved. Terminating.')

if __name__ == "__main__":
    main()
