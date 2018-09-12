"""This module contains the functions for handling a participant's guesses."""
from datetime import datetime, timedelta
from collections import deque, OrderedDict

import jstyleson

from . import settings
from .database import DbStreamer, SessionLogEntry

def _remove_stale_guesses(guess_queue, username):
    new_queue = deque()
    expiration = datetime.now() - timedelta(minutes=15)
    for guess in guess_queue:
        if guess['timestamp'] < expiration:
            continue
        if guess['username'] == username:
            continue
        new_queue.append(guess)
    return new_queue

def do_extra_guess(user, locations, item_type, participant, guessing_game):
    """Adds a participant's extra guess to the queue and creates a session log entry."""
    logger = settings.init_logger(__name__)
    now = datetime.now()
    for extra_items in guessing_game.guessables.extras:
        if not item_type == extra_items.get_type():
            continue
        for location in locations:
            if not extra_items.get_location(location):
                logger.debug('%s is not a valid item for %s guess', location, item_type)
                return
        guessing_game.guesses[item_type] = _remove_stale_guesses(
            guessing_game.guesses[item_type], user['username']
        )
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
        guess = SessionLogEntry(
            timestamp=now,
            participant=participant.user_id,
            participant_name=participant.username,
            guess_type=item_type,
            guess=jstyleson.dumps(extra_guess).replace(',', '\n'),
            session_points=participant.session_points,
            total_points=participant.total_points
        )
        extra_guess['user-id'] = user['user-id']
        extra_guess['username'] = user['username']
        extra_guess['timestamp'] = now
        guessing_game.guesses[item_type].append(extra_guess)
        guessing_game.state['database']['current-session'].guesses.append(guess)
        logger.debug('Extra Item Guess: %s', extra_guess)
        return
    logger.info("Extra item type %s does not exist", item_type)

def do_item_guess(user, item, participant, guessing_game):
    """Adds a participant's item guess to the queue and creates a session log entry."""
    logger = settings.init_logger(__name__)
    if not item:
        return
    guessing_game.guesses['items'] = _remove_stale_guesses(
        guessing_game.guesses['items'], user['username'])
    now = datetime.now()
    item_guess = {
        "timestamp": now,
        "user-id": user['user-id'],
        "username": user['username'],
        "guess": item
    }
    guess = SessionLogEntry(
        timestamp=datetime.now(),
        participant=participant.user_id,
        participant_name=participant.username,
        guess_type="Item",
        guess=item,
        session_points=participant.session_points,
        total_points=participant.total_points
    )
    guessing_game.guesses['items'].append(item_guess)
    guessing_game.state['database']['current-session'].guesses.append(guess)
    logger.info('%s Item %s guessed by user %s', now, item, user['username'])
    logger.debug(item_guess)

def complete_guess(guessing_game, item):
    """Completes Item guess."""
    if not guessing_game.state['running']:
        guessing_game.logger.info('Guessing game not running')
        return
    if not item:
        return
    expiration = datetime.now() - timedelta(minutes=15)
    new_guess_deque = deque()
    first_guess = False
    for guess in guessing_game.guesses['items']:
        if guess['timestamp'] < expiration:
            continue
        if guess['guess'] is not item:
            new_guess_deque.append(guess)
            continue
        if not first_guess:
            DbStreamer.objects.filter( #pylint: disable=no-member
                channel_id=guessing_game.state['database']['streamer'].channel_id,
                participants__user_id=guess['user-id']).update(
                    inc__participants__S__session_points=
                    guessing_game.state['database']['streamer'].first_bonus,
                    inc__participants__S__total_points=
                    guessing_game.state['database']['streamer'].first_bonus)
            guessing_game.logger.info(
                'User %s made the first correct guess earning %s extra points',
                guess['username'], guessing_game.state['database']['streamer'].first_bonus)
            first_guess = True
        DbStreamer.objects.filter( #pylint: disable=no-member
            channel_id=guessing_game.state['database']['streamer'].channel_id,
            participants__user_id=guess['user-id']).modify(
                inc__participants__S__session_points=
                guessing_game.state['database']['streamer'].points,
                inc__participants__S__total_points=
                guessing_game.state['database']['streamer'].points)
        guessing_game.logger.info(
            'User %s guessed correctly and earned %s points',
            guess['username'], guessing_game.state['database']['streamer'].points)
        guessing_game.guesses['items'] = new_guess_deque
        guessing_game.logger.info('Guesses completed')

def complete_extra_guess(guessing_game, command):
    """Completes Extra Items guess."""
    logger = settings.init_logger(__name__)
    if len(command) < 3:
        logger.info('Extra item guess completion command too short')
        return
    extra_items_type = command[0]
    for extra_items in guessing_game.guessables.extras:
        if not extra_items_type == extra_items.get_type():
            continue
        final_item = extra_items.get_item(command[1])
        if not final_item:
            logger.info("Extra item type %s does not have an item with code %s",
                        extra_items_type, command[1])
            return
        final_location = extra_items.get_location(command[2])
        if not final_location:
            logger.info("Extra item type %s does not have a location with code %s",
                        extra_items_type, command[2])
            return
        logger.info('%s is at %s', final_item, final_location)
        guessing_game.state[extra_items_type][final_item] = final_location
        guessing_game.logger.debug(guessing_game.state[extra_items_type])
        if len(guessing_game.state[extra_items_type]) == extra_items.get_count():
            logger.info("Completing %s guesses", extra_items_type)
            for guess in guessing_game.guesses[extra_items_type]:
                count = 0
                for final in guessing_game.state[extra_items_type]:
                    if guess[final] == guessing_game.state[extra_items_type][final]:
                        count += 1
                DbStreamer.objects.filter( #pylint: disable=no-member
                    channel_id=guessing_game.state['database']['streamer'].channel_id,
                    participants__user_id=guess['user-id']).modify(
                        inc__participants__S__session_points=
                        guessing_game.state['database']['streamer'].points * count,
                        inc__participants__S__total_points=
                        guessing_game.state['database']['streamer'].points * count)
                guessing_game.logger.info(
                    'User %s guessed %s medals correctly and earned %s points',
                    guess['username'], count,
                    guessing_game.state['database']['streamer'].points * count)
                if count == extra_items.get_count():
                    DbStreamer.objects.filter( #pylint: disable=no-member
                        channel_id=guessing_game.state['database']['streamer'].channel_id,
                        participants__user_id=guess['user-id']).update(
                            inc__participants__S__session_points=
                            guessing_game.state['database']['streamer'].first_bonus,
                            inc__participants__S__total_points=
                            guessing_game.state['database']['streamer'].first_bonus)
                    guessing_game.logger.info(
                        'User %s guessed all medals correctly and earned %s bonus points',
                        guess['username'],
                        guessing_game.state['database']['streamer'].first_bonus)
                guessing_game.state['database']['streamer'].save()
                guessing_game.guesses[extra_items_type] = deque()
                message = '%s guesses completed' % extra_items_type
                guessing_game.logger.info(message)
                return
        return
    logger.info("Extra item type %s does not exist", extra_items_type)
