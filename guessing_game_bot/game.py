"""The module for the GuessingGame class."""
from collections import deque, OrderedDict
from datetime import datetime, timedelta
import jstyleson
from . import settings
from .guessable import Guessables
from .reports import Reports

class GuessingGame():
    """A class that manages the GuessingGame."""

    def __init__(self, modes, multi_guess):
        self.__logger = settings.init_logger(__name__)
        self.__guess_log = deque()
        self.__reports = Reports()
        self.__guessables = Guessables(modes, multi_guess)
        self.__running = False
        self.__mode = []
        self.__guesses = {
            "items": deque()
        }
        for guess_type in multi_guess:
            self.__guesses[guess_type] = deque()
            setattr(self, '__%s' % guess_type, {})

    def reset_modes(self, user):
        """Reset active guessing game modes."""

        message = 'Mode reset to normal by %s' % user['username']
        self.__mode.clear()
        self.__logger.info(message)
        return message

    def add_mode(self, mode, user):
        """Add a mode to the guessing game's active modes.

        Arguments:
            mode {string} -- Name of the mode
            user {dict} -- User who initiated adding the command

        Returns:
            string -- A message to send to Twitch chat
        """
        if self.__running:
            self.__logger.info('Guessing game already started')
            return None
        for modes in self.__guessables.modes:
            if mode == modes.name and mode not in self.__mode:
                message = 'Mode %s added by %s' % (mode, user['username'])
                self.__mode += [mode]
                self.__logger.info(message)
                return message
        return None

    def remove_mode(self, mode, user):
        """Remove a mode from the guessing game's active modes.

        Arguments:
            mode {string} -- Name of the mode
            user {dict} -- User who initiated adding the command

        Returns:
            string -- A message to send to Twitch chat
        """

        if self.__running:
            self.__logger.info('Guessing game already started')
            return None
        if mode in self.__mode:
            message = 'Mode %s removed by %s' % (mode, user['username'])
            self.__mode.remove(mode)
            self.__logger.info(message)
            return message
        return None

    def start_guessing_game(self, user, items):
        """Starts a guessing game.

        Arguments:
            user {string} -- The user who initiated the guessing game
            items {dict} -- The guessable items for the guessing game

        Returns:
            string -- A message sent to Twitch chat mentioning who initiated the guessing game
        """

        if self.__running:
            self.__logger.info('Guessing game already running')
            return None
        self.__guessables.items = (items, self.__mode)
        self.__running = True
        message = 'Guessing game started by %s' % user['username']
        self.__logger.info(message)
        return message

    def end_guessing_game(self, user):
        """Ends a guessing game."""

        if not self.__running:
            self.__logger.info('Guessing game not running')
            return None
        self.__running = False
        self.__mode.clear()
        for queues in self.__guesses:
            self.__guesses[queues] = deque()
            if queues == 'items':
                continue
            setattr(self, '__%s' % queues, deque())
        # self.state['songs'].clear()
        # self.state['medals'].clear()
        self.__reports.write_guess_report(self.__guess_log)
        message = 'Guessing game ended by %s' % user['username']
        self.__logger.info(message)
        return message

    def report_totals(self, participants):
        """Creates a CSV containing the total points of all of a streamer's participants.

        Arguments:
            participants {list} -- A list of all of a streamer's participants
        """

        self.__reports.write_totals_report(participants)

    def guess(self, guesser, command):
        """Tracks a user's guess.

        Arguments:
            guesser {Participant} -- The participant making the guess
            command {list} -- Guess items
        """

        if len(command) > 2 and not self.__running:
            self.__is_extra_guess(guesser, command[0], command[1:])
        if not self.__running:
            return
        command_value = command[0].lower()
        item = self.__guessables.get_item(command_value)
        if not item:
            self.__logger.info('Item %s not found', command_value)
        self.__item_guess(guesser, item)

    def complete_guess(self, streamer, command):
        """Processes a guess being completed."""

        if len(command) > 1:
            subcommand_name = command[0]
            if subcommand_name not in self.__guessables.extra_item_types:
                return
            self.__set_extra_guess_final(subcommand_name, command[1], command[2])
            extra_items_final = getattr(self, '__%s' % subcommand_name)
            for extra_item in self.__guessables.extras:
                if not extra_item.get_type() == subcommand_name:
                    continue
                if len(extra_items_final) == extra_item.get_count():
                    message = '%s guesses completed' % subcommand_name
                    self.__complete_extra_guess(
                        streamer, subcommand_name, extra_items_final)
                    extra_items_final.clear()
                    self.__guesses[subcommand_name] = deque()
                    self.__logger.info(message)
                    streamer.save()
            return
        item = command[0]
        self.__complete_item_guess(streamer, item)
        return

    def __set_extra_guess_final(self, guess_type, item, location):
        extra_items_type = guess_type
        for extra_items in self.__guessables.extras:
            if not extra_items_type == extra_items.get_type():
                continue
            final_item = extra_items.get_item(item)
            if not final_item:
                self.__logger.info("Extra item type %s does not have an item with code %s",
                                   extra_items_type, item)
                return
            final_location = extra_items.get_location(location)
            if not final_location:
                self.__logger.info("Extra item type %s does not have a location with code %s",
                                   extra_items_type, location)
                return
            self.__logger.info('%s is at %s', final_item, final_location)
            final_item_dict = getattr(self, '__%s' % extra_items_type)
            final_item_dict[final_item] = final_location
            self.__logger.debug(final_item_dict)
            return
        self.__logger.info("Extra item type %s does not exist", extra_items_type)

    def __item_guess(self, guesser, item):
        if not item:
            return
        self.__guesses['items'] = self.__remove_stale_guesses(
            self.__guesses['items'], guesser.username)
        now = datetime.now()
        item_guess = {
            "timestamp": now,
            "user-id": guesser.user_id,
            "username": guesser.username,
            "guess": item
        }
        guess = dict(
            timestamp=datetime.now(),
            participant=guesser.user_id,
            participant_name=guesser.username,
            guess_type="Item",
            guess=item,
            session_points=guesser.session_points,
            total_points=guesser.total_points)
        self.__guesses['items'].append(item_guess)
        self.__guess_log.append(guess)
        self.__logger.info('%s Item %s guessed by user %s', now, item, guesser.username)
        self.__logger.debug(item_guess)

    def __complete_item_guess(self, streamer, item):
        if not self.__running:
            self.__logger.info('Guessing game not running')
            return
        item = item.lower()
        item = self.__guessables.get_item(item)
        if not item:
            self.__logger.info('Item %s not found', item)
        expiration = datetime.now() - timedelta(minutes=15)
        new_guess_deque = deque()
        first_guess = False
        for guess in self.__guesses['items']:
            if guess['timestamp'] < expiration:
                continue
            if guess['guess'] is not item:
                new_guess_deque.append(guess)
                continue
            if not first_guess:
                for participant in streamer.participants:
                    if participant.user_id == guess['user-id']:
                        participant.session_points += streamer.first_bonus
                        self.__logger.info(
                            'User %s made the first correct guess earning %s bonus points',
                            guess['username'], streamer.first_bonus)
                first_guess = True
            for participant in streamer.participants:
                if participant.user_id == guess['user-id']:
                    participant.session_points += streamer.points
                    self.__logger.info(
                        'User %s made a correct guess earning %s points',
                        guess['username'], streamer.points)
            self.__guesses['items'] = new_guess_deque
            self.__logger.info('Guesses completed')

    def __is_extra_guess(self, guesser, extra_type, extra_guess):
        self.__logger.debug(
            'Item type: %s, Location value: %s', extra_type, extra_guess)
        if extra_type in self.__guessables.extra_item_types:
            self.__extra_guess(extra_guess, extra_type, guesser)

    def __extra_guess(self, locations, item_type, guesser):
        """Adds a guesser's extra guess to the queue and creates a session log entry."""
        logger = settings.init_logger(__name__)
        now = datetime.now()
        for extra_items in self.__guessables.extras:
            if not item_type == extra_items.get_type():
                continue
            for location in locations:
                if not extra_items.get_location(location):
                    logger.debug('%s is not a valid item for %s guess', location, item_type)
                    return
            self.__guesses[item_type] = self.__remove_stale_guesses(
                self.__guesses[item_type], guesser.username)
            extra_guess = OrderedDict()
            for item in extra_items.get_items():
                extra_guess[item] = None
            i = 0
            for extra in extra_guess:
                guess = locations[i]
                if not any(guess in s for s in extra_items.get_locations().values()):
                    logger.info('Invalid location %s', guess)
                    return
                extra_guess[extra] = extra_items.get_location(guess)
                if i >= len(extra_guess):
                    break
                i += 1
            guess = dict(
                timestamp=now,
                guesser=guesser.user_id,
                participant_name=guesser.username,
                guess_type=item_type,
                guess=jstyleson.dumps(extra_guess).replace(',', '\n'),
                session_points=guesser.session_points,
                total_points=guesser.total_points)
            extra_guess['user-id'] = guesser.user_id
            extra_guess['username'] = guesser.username
            extra_guess['timestamp'] = now
            self.__guesses[item_type].append(extra_guess)
            self.__guess_log.append(guess)
            logger.debug('Extra Item Guess: %s', extra_guess)
            return
        logger.info("Extra item type %s does not exist", item_type)

    def __complete_extra_guess(self, streamer, item_type, guesses):
        self.__logger.info("Completing %s guesses", item_type)
        for guess in self.__guesses[item_type]:
            count = 0
            for final in guesses:
                if guess[final] == guesses[final]:
                    count += 1
            for participant in streamer.participants:
                if participant.user_id == guess['user-id']:
                    earned_points = streamer.points * count
                    participant.session_points += earned_points
                    participant.total_points += earned_points
                    self.__logger.info(
                        'User %s guessed %s medals correctly and earned %s points',
                        guess['username'], count,
                        earned_points)
                    if count == len(guesses):
                        bonus_points = streamer.first_bonus
                        participant.session_points += bonus_points
                        participant.total_points += bonus_points
                        self.__logger.info(
                            'User %s guessed all medals correctly and earned %s bonus points',
                            guess['username'],
                            bonus_points)

    @staticmethod
    def __remove_stale_guesses(guess_queue, username):
        new_queue = deque()
        expiration = datetime.now() - timedelta(minutes=15)
        for guess in guess_queue:
            if guess['timestamp'] < expiration:
                continue
            if username and guess['username'] == username:
                continue
            new_queue.append(guess)
        return new_queue
