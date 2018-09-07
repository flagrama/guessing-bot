"""This module contains the functions for handling a participant's guesses."""
from datetime import datetime, timedelta
from collections import deque, OrderedDict

import jstyleson

from database import SessionLogEntry
import settings

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

def do_item_guess(user, item, participant, guessing_game):
    """Adds a participant's item guess to the queue and creates a session log entry."""
    logger = settings.init_logger(__name__)
    if not item:
        logger.info('Item %s not found', item)
        return
    guessing_game.guesses['item'] = _remove_stale_guesses(
        guessing_game.guesses['item'], user['username'])
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
    guessing_game.guesses['item'].append(item_guess)
    guessing_game.state['database']['current-session'].guesses.append(guess)
    logger.info('%s Item %s guessed by user %s', now, item, user['username'])
    logger.debug(item_guess)

def do_medal_guess(user, medals, participant, guessing_game):
    """Adds a participant's medal guess to the queue and creates a session log entry."""
    logger = settings.init_logger(__name__)
    if len(medals) < 5 or len(medals) < 6 and not guessing_game.state['freebie']:
        logger.info('Medal command incomplete')
        logger.debug(medals)
        return
    guessing_game.guesses['medal'] = _remove_stale_guesses(
        guessing_game.guesses['medal'], user['username'])
    medal_guess = OrderedDict()
    medal_guess["forest"] = None
    medal_guess["fire"] = None
    medal_guess["water"] = None
    medal_guess["spirit"] = None
    medal_guess["shadow"] = None
    medal_guess["light"] = None
    i = 0
    for medal in medal_guess:
        guess = medals[i]
        if guess not in guessing_game.state['guessables']['dungeons'] and guess != 'free':
            logger.info('Invalid medal %s', guess)
            return None, None
        if medal == guessing_game.state['freebie'] or guess == 'free':
            continue
        medal_guess[medal] = guess
        i += 1
    guess = SessionLogEntry(
        timestamp=datetime.now(),
        participant=participant.user_id,
        participant_name=participant.username,
        guess_type="Medal",
        guess=jstyleson.dumps(medal_guess).replace(',', '\n'),
        session_points=participant.session_points,
        total_points=participant.total_points
    )
    medal_guess['user-id'] = user['user-id']
    medal_guess['username'] = user['username']
    medal_guess['timestamp'] = datetime.now()
    guessing_game.guesses['song'].append(medal_guess)
    guessing_game.state['database']['current-session'].guesses.append(guess)
    logger.debug('Medal Guess: %s', medal_guess)

def do_song_guess(user, songs, participant, guessing_game):
    """Adds a participant's song guess to the queue and creates a session log entry."""
    logger = settings.init_logger(__name__)
    if len(songs) < 12:
        logger.info('song command incomplete')
        logger.debug(songs)
        return None, None
    guessing_game.guesses['song'] = _remove_stale_guesses(
        guessing_game.guesses['song'], user['username'])
    song_guess = OrderedDict()
    song_guess["Zelda's Lullaby"] = None
    song_guess["Epona's Song"] = None
    song_guess["Saria's Song"] = None
    song_guess["Sun's Song"] = None
    song_guess["Song of Time"] = None
    song_guess["Song of Storms"] = None
    song_guess["Minuet of Forest"] = None
    song_guess["Bolero of Fire"] = None
    song_guess["Serenade of Water"] = None
    song_guess["Requiem of Spirit"] = None
    song_guess["Nocturne of Shadow"] = None
    song_guess["Prelude of Light"] = None
    i = 0
    for song in song_guess:
        guess = songs[i]
        songname = guessing_game.parse_songs(guess)
        if not songname:
            logger.info('Invalid song %s', guess)
            return
        song_guess[song] = songname
        i += 1
    guess = SessionLogEntry(
        timestamp=datetime.now(),
        participant=participant.user_id,
        participant_name=participant.username,
        guess_type="Song",
        guess=jstyleson.dumps(song_guess).replace(',', '\n'),
        session_points=participant.session_points,
        total_points=participant.total_points
    )
    song_guess['user-id'] = user['user-id']
    song_guess['username'] = user['username']
    song_guess['timestamp'] = datetime.now()
    guessing_game.guesses['song'].append(song_guess)
    guessing_game.state['database']['current-session'].guesses.append(guess)
    logger.debug(song_guess)
