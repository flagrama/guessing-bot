import argparse
import logging

import settings
import bot

def main(debug):
    settings.DEBUG = debug
    client = bot.TwitchBot()
    client.start()

if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(\
        description='A bot for making a game of guessing upcoming items in \
        randomizers.')
    parser.add_argument('--debug', dest='debug', action='store_true', default=False)
    args = parser.parse_args()

    try:
        main(args.debug)
    except KeyboardInterrupt:
        print('\n')
        logger.info('SIGINT recieved. Terminating.')
