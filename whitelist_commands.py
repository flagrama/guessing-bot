"""This moudle contains the functions for managing the streamer's whitelist and blacklist."""
from functools import partial
import mongoengine

from database import Streamer, BlacklistUser, WhitelistUser
import twitch
import settings

def _get_username_from_command(command):
    try:
        username = command[2]
        return username
    except IndexError:
        return False

def _add_whitelist_command(command, streamer, channel_id):
    logger = settings.init_logger(__name__)
    message = 'Unable to add user to whitelist'
    username = _get_username_from_command(command)

    if not username:
        logger.error('Username not provided')
        return message

    new_user_id = twitch.get_user_id(username)
    if not new_user_id:
        return message

    new_user = WhitelistUser(username=username, user_id=new_user_id)
    try:
        db_streamer = Streamer.objects.get(channel_id=channel_id, #pylint: disable=no-member
                                           whitelist__user_id=new_user_id)
        if db_streamer.whitelist:
            logger.info('User with ID %s already exists in the database', new_user_id)
            return message
    except Streamer.DoesNotExist: #pylint: disable=no-member
        logger.error('User with ID %s does not exist in the database', new_user_id)
    try:
        streamer.whitelist.append(new_user)
        streamer.save()
        streamer.reload()
        message = 'User %s added to whitelist' % command[2]
        logger.info(message)
        return message
    except mongoengine.NotUniqueError:
        logger.error('User with ID %s already exists in the database', new_user_id)
        return message


def _remove_whitelist_command(command, streamer, channel_id):
    logger = settings.init_logger(__name__)
    message = 'Unable to remove user from whitelist'
    username = _get_username_from_command(command)

    if not username:
        logger.error('Username not provided')
        return message

    existing_user_id = twitch.get_user_id(username)
    if not existing_user_id:
        return message

    try:
        db_streamer = Streamer.objects.get(channel_id=channel_id, #pylint: disable=no-member
                                           whitelist__user_id=existing_user_id)
        if not db_streamer.whitelist:
            return message
        Streamer.objects.update(channel_id=channel_id, #pylint: disable=no-member
                                pull__whitelist__user_id=existing_user_id)
        streamer.save()
        streamer.reload()
        message = 'User %s removed from whitelist' % command[2]
        logger.info(message)
        return message
    except Streamer.DoesNotExist: #pylint: disable=no-member
        logger.error('User with ID %s does not exist in the database', existing_user_id)
        return message


def _add_blacklist_command(command, streamer, channel_id):
    logger = settings.init_logger(__name__)
    message = 'Unable to add user to whitelist'
    username = _get_username_from_command(command)

    if not username:
        logger.error('Username not provided')
        return message

    new_user_id = twitch.get_user_id(username)
    if not new_user_id:
        return message

    new_user = BlacklistUser(username=username, user_id=new_user_id)
    try:
        db_streamer = Streamer.objects.get(channel_id=channel_id, #pylint: disable=no-member
                                           blacklist__user_id=new_user_id)
        if db_streamer.blacklist:
            logger.info('User with ID %s already exists in the database', new_user_id)
            return message
    except Streamer.DoesNotExist: #pylint: disable=no-member
        logger.error('User with ID %s does not exist in the database', new_user_id)

    try:
        streamer.blacklist.append(new_user)
        streamer.save()
        streamer.reload()
        message = 'User %s added to blacklist' % command[2]
        logger.info(message)
        return message
    except mongoengine.NotUniqueError:
        logger.error('User with ID %s already exists in the database', new_user_id)
        return message


def _remove_blacklist_command(command, streamer, channel_id):
    logger = settings.init_logger(__name__)
    message = 'Unable to remove user from blacklist'
    username = _get_username_from_command(command)

    if not username:
        logger.error('Username not provided')
        return message

    existing_user_id = twitch.get_user_id(username)
    if not existing_user_id:
        return message

    try:
        db_streamer = Streamer.objects.get(channel_id=channel_id, #pylint: disable=no-member
                                           blacklist__user_id=existing_user_id)
        if not db_streamer.whitelist:
            return message
        Streamer.objects.update(channel_id=channel_id, #pylint: disable=no-member
                                pull__blacklist__user_id=existing_user_id)
        streamer.save()
        streamer.reload()
        message = 'User %s removed from blacklist' % command[2]
        logger.info(message)
        return message
    except Streamer.DoesNotExist: #pylint: disable=no-member
        logger.error('User with ID %s does not exist in the database', existing_user_id)
        return message

def do_whitelist_command(command, streamer, channel_id):
    """Calls the command function the user invokes."""
    logger = settings.init_logger(__name__)
    commands = {
        "add": partial(_add_whitelist_command),
        "remove": partial(_remove_whitelist_command),
        "ban": partial(_add_blacklist_command),
        "unban": partial(_remove_blacklist_command)
    }
    try:
        command_name = command[1]
        if command_name in commands:
            return commands[command_name](command, streamer, channel_id)
    except IndexError:
        logger.error('Command missing arguments')
        return None
    except KeyError:
        logger.error('Command missing')
        return None
    return None
