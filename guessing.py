"""This module contains the functions for handling a participant's guesses."""
from datetime import datetime, timedelta
from collections import deque, OrderedDict

import jstyleson

from database import Streamer, SessionLogEntry
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
            return
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
        return
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

def complete_guess(guessing_game, item):
    """Completes Item guess."""
    if not guessing_game.state['running']:
        guessing_game.logger.info('Guessing game not running')
        return
    if not item:
        guessing_game.logger.info('Item %s not found', item)
        return
    expiration = datetime.now() - timedelta(minutes=15)
    new_guess_deque = deque()
    first_guess = False
    for guess in guessing_game.guesses['item']:
        if guess['timestamp'] < expiration:
            continue
        if guess['guess'] is not item:
            new_guess_deque.append(guess)
            continue
        if not first_guess:
            Streamer.objects.filter( #pylint: disable=no-member
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
        Streamer.objects.filter( #pylint: disable=no-member
            channel_id=guessing_game.state['database']['streamer'].channel_id,
            participants__user_id=guess['user-id']).modify(
                inc__participants__S__session_points=
                guessing_game.state['database']['streamer'].points,
                inc__participants__S__total_points=
                guessing_game.state['database']['streamer'].points)
        guessing_game.logger.info(
            'User %s guessed correctly and earned %s points',
            guess['username'], guessing_game.state['database']['streamer'].points)
        guessing_game.guesses['item'] = new_guess_deque
        guessing_game.logger.info('Guesses completed')

def complete_medal_guess(guessing_game, command):
    """Completes Medal guess."""
    if len(command) < 2:
        return None
    if command[1] not in guessing_game.state['guessables']['dungeons']:
        if not guessing_game.state['running'] and command[1] == 'free':
            guessing_game.state['freebie'] = command[0]
            guessing_game.logger.info('Medal %s set to freebie', command[0])
        return None
    if command[0] in guessing_game.state['guessables']['medals']:
        if command[0] in guessing_game.state['medals']:
            guessing_game.logger.info('Medal %s already in guesses')
            if guessing_game.state['medals'][command[0]] != command[1]:
                guessing_game.state['medals'][command[0]] = command[1]
                guessing_game.logger.info('Medal %s set to dungeon %s', command[0], command[1])
        guessing_game.state['medals'][command[0]] = command[1]
        guessing_game.logger.info('Medal %s set to dungeon %s', command[0], command[1])
    if ((guessing_game.state['freebie'] and len(guessing_game.state['medals']) == 5)
            or len(guessing_game.state['medals']) == 6):
        local_guesses = deque()
        hiscore = 0
        for guess in guessing_game.guesses['medal']:
            count = 0
            for final in guessing_game.state['medals']:
                if guess[final] == guessing_game.state['medals'][final]:
                    count += 1
            localguess = {
                "user-id": guess['user-id'], "username": guess['username'], "correct": count
                }
            local_guesses.append(localguess)
            if count > hiscore:
                hiscore = count
        if hiscore < 1:
            return None
        for guesser in local_guesses:
            if guesser['correct'] < hiscore:
                continue
            try:
                streamer = Streamer.objects.get( #pylint: disable=no-member
                    channel_id=guessing_game.state['database']['channel-id'],
                    participants__user_id=guesser['user-id'])
            except Streamer.DoesNotExist: #pylint: disable=no-member
                guessing_game.logger.error('Participant with ID %s does not exist in the database',
                                           guesser['user-id'])
                return "User %s does not exist." % guesser['username']
            for update_participant in streamer.participants:
                if update_participant.user_id == int(guesser['user-id']):
                    update_participant.session_points += hiscore
                    update_participant.total_points += hiscore
            guessing_game.logger.info('User %s guessed correctly and earned %s points',
                                      guesser['username'], hiscore)
            streamer.save()
            streamer.reload()
            guessing_game.guesses['medal'] = deque()
            guessing_game.logger.info('Medal guesses completed')
    return None

def complete_song_guess(guessing_game, command):
    """Completes Song guess."""
    if len(command) < 2:
        guessing_game.logger.info('Not enough arguments for song')
        return None
    new_song = guessing_game.parse_songs(command[0])
    new_location = guessing_game.parse_songs(command[1])
    if not new_song or not new_location:
        return None
    if new_song in guessing_game.state['guessables']['songs']:
        if new_song in guessing_game.state['songs']:
            guessing_game.logger.info('Song %s already in guesses')
            if guessing_game.state['songs'][new_song] != new_location:
                guessing_game.state['songs'][new_song] = new_location
                guessing_game.logger.info('Song %s set to location %s', new_song, new_location)
        guessing_game.state['songs'][new_song] = new_location
        guessing_game.logger.info('Song %s set to location %s', new_song, new_location)
    if len(guessing_game.state['songs']) == 12:
        local_guesses = deque()
        hiscore = 0
        for guess in guessing_game.guesses['song']:
            count = 0
            for final in guessing_game.state['songs']:
                if guessing_game.parse_songs(guess[final]) == guessing_game.state['songs'][final]:
                    count += 1
            localguess = {
                "user-id": guess['user-id'], "username": guess['username'], "correct": count
                }
            local_guesses.append(localguess)
            if count > hiscore:
                hiscore = count
        if hiscore < 1:
            return None
        for guesser in local_guesses:
            if guesser['correct'] < hiscore:
                continue
            try:
                streamer = Streamer.objects.get( #pylint: disable=no-member
                    channel_id=guessing_game.state['database']['channel-id'],
                    participants__user_id=guesser['user-id'])
            except Streamer.DoesNotExist: #pylint: disable=no-member
                guessing_game.logger.error('Participant with ID %s does not exist in the database',
                                           guesser['user-id'])
                return "User %s does not exist." % guesser['username']
            for update_participant in streamer.participants:
                if update_participant.user_id == int(guesser['user-id']):
                    update_participant.session_points += hiscore
                    update_participant.total_points += hiscore
            guessing_game.logger.info('User %s guessed correctly and earned %s points',
                                      guesser['username'], hiscore)
            streamer.save()
            streamer.reload()
            guessing_game.guesses['song'] = deque()
            guessing_game.logger.info('Song guesses completed')
    return None
