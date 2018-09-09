"""This module contains the functions for handling a participant's guesses."""
from datetime import datetime, timedelta
from collections import deque, OrderedDict

import jstyleson

from database import DbStreamer, SessionLogEntry
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
    medal_guess["Forest Medallion"] = None
    medal_guess["Fire Medallion"] = None
    medal_guess["Water Medallion"] = None
    medal_guess["Spirit Medallion"] = None
    medal_guess["Shadow Medallion"] = None
    medal_guess["Light Medallion"] = None
    i = 0
    for medal in medal_guess:
        guess = medals[i]
        if not any(guess in s for s in guessing_game.state['guessables']['dungeons'].values()):
            logger.info('Invalid dungeon %s', guess)
            return
        medal_guess[medal] = _get_dungeon_name(guess, guessing_game)
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
    guessing_game.guesses['medal'].append(medal_guess)
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
        guessing_game.guesses['item'] = new_guess_deque
        guessing_game.logger.info('Guesses completed')

def _get_medal_name(code, guessing_game):
    for name, codes in guessing_game.state['guessables']['medals'].items():
        if code in codes:
            return name
    return None

def _get_dungeon_name(code, guessing_game):
    for name, codes in guessing_game.state['guessables']['dungeons'].items():
        if code in codes:
            return name
    return None

def complete_medal_guess(guessing_game, command):
    """Completes Medal guess."""
    if len(command) < 2:
        guessing_game.logger.debug('Medal guess completion command too short')
        return None
    guessed_medal = command[0]
    guessed_location = command[1]
    guessing_game.logger.info('%s is at %s', guessed_medal, guessed_location)
    this_medal = _get_medal_name(guessed_medal, guessing_game)
    this_dungeon = _get_dungeon_name(guessed_location, guessing_game)
    if this_medal and this_dungeon:
        guessing_game.state['medals'][this_medal] = this_dungeon
        guessing_game.logger.debug(guessing_game.state['medals'])
    if len(guessing_game.state['medals']) == 6:
        guessing_game.logger.info('Completing medal guesses')
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
                streamer = DbStreamer.objects.get( #pylint: disable=no-member
                    channel_id=guessing_game.state['database']['channel-id'],
                    participants__user_id=guesser['user-id'])
            except DbStreamer.DoesNotExist: #pylint: disable=no-member
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
            message = 'Medal guesses completed'
            guessing_game.logger.info(message)
            return message
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
            guessing_game.logger.info('Song %s already in guesses', new_song)
            if guessing_game.state['songs'][new_song] != new_location:
                guessing_game.state['songs'][new_song] = new_location
                guessing_game.logger.info('Song %s set to location %s', new_song, new_location)
                return
        guessing_game.state['songs'][new_song] = new_location
        guessing_game.logger.info('Song %s set to location %s', new_song, new_location)
        guessing_game.logger.debug(guessing_game.state['songs'])
    if len(guessing_game.state['songs']) == 12:
        guessing_game.logger.info('Finishing song guesses')
        local_guesses = deque()
        hiscore = 0
        for guess in guessing_game.guesses['song']:
            count = 0
            for final in guessing_game.state['songs']:
                if guess[final] == guessing_game.state['songs'][final]:
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
                streamer = DbStreamer.objects.get( #pylint: disable=no-member
                    channel_id=guessing_game.state['database']['channel-id'],
                    participants__user_id=guesser['user-id'])
            except DbStreamer.DoesNotExist: #pylint: disable=no-member
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
