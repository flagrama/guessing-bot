import argparse

import bot

def main():
    parser = argparse.ArgumentParser(\
        description='A bot for making a game of guessing upcoming items in \
        randomizers.')
    parser.add_argument('--debug', dest='debug', action='store_true', default=False)
    args = parser.parse_args()

    client = bot.TwitchBot(args.debug)
    client.start()

if __name__ == "__main__":
    main()
