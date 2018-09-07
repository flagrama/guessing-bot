"""This moudle contains the functions for managing the streamer's whitelist and blacklist."""
from functools import partial
import mongoengine

from database import Streamer, BlacklistUser, WhitelistUser
import twitch
import settings

LOGGER = settings.init_logger(__name__)

def _get_username_from_command(command):
    try:
        username = command[2]
        return username
    except IndexError:
        return False

def _add_user_to_whitelist(command, streamer, channel_id):
    message = 'Unable to add user to whitelist'
    username = _get_username_from_command(command)

    if not username:
        LOGGER.error('Username not provided')
        return message

    new_user_id = twitch.get_user_id(username)
    if not new_user_id:
        return message

    new_user = WhitelistUser(username=username, user_id=new_user_id)
    try:
        db_streamer = Streamer.objects.get(channel_id=channel_id, #pylint: disable=no-member
                                           whitelist__user_id=new_user_id)
        if db_streamer.whitelist:
            LOGGER.info('User with ID %s already exists in the database', new_user_id)
            return message
    except Streamer.DoesNotExist: #pylint: disable=no-member
        LOGGER.error('User with ID %s does not exist in the database', new_user_id)
    try:
        streamer.whitelist.append(new_user)
        streamer.save()
        streamer.reload()
        message = 'User %s added to whitelist' % command[2]
        LOGGER.info(message)
        return message
    except mongoengine.NotUniqueError:
        LOGGER.error('User with ID %s already exists in the database', new_user_id)
    return message


def _remove_user_from_whitelist(command, streamer, channel_id):
    message = 'Unable to remove user from whitelist'
    username = _get_username_from_command(command)

    if not username:
        LOGGER.error('Username not provided')
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
        LOGGER.info(message)
        return message
    except Streamer.DoesNotExist: #pylint: disable=no-member
        LOGGER.error('User with ID %s does not exist in the database', existing_user_id)
        return message


def _add_user_to_blacklist(command, streamer, channel_id):
    message = 'Unable to add user to whitelist'
    username = _get_username_from_command(command)

    if not username:
        LOGGER.error('Username not provided')
        return message

    new_user_id = twitch.get_user_id(username)
    if not new_user_id:
        return message

    new_user = BlacklistUser(username=username, user_id=new_user_id)
    try:
        db_streamer = Streamer.objects.get(channel_id=channel_id, #pylint: disable=no-member
                                           blacklist__user_id=new_user_id)
        if db_streamer.blacklist:
            LOGGER.info('User with ID %s already exists in the database', new_user_id)
            return message
    except Streamer.DoesNotExist: #pylint: disable=no-member
        LOGGER.error('User with ID %s does not exist in the database', new_user_id)

    try:
        streamer.blacklist.append(new_user)
        streamer.save()
        streamer.reload()
        message = 'User %s added to blacklist' % command[2]
        LOGGER.info(message)
        return message
    except mongoengine.NotUniqueError:
        LOGGER.error('User with ID %s already exists in the database', new_user_id)
    return message


def _remove_user_from_blacklist(command, streamer, channel_id):
    message = 'Unable to remove user from blacklist'
    username = _get_username_from_command(command)

    if not username:
        LOGGER.error('Username not provided')
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
        LOGGER.info(message)
        return message
    except Streamer.DoesNotExist: #pylint: disable=no-member
        LOGGER.error('User with ID %s does not exist in the database', existing_user_id)
        return message

def do_whitelist_command(command, streamer, channel_id):
    """Calls the command function the user invokes."""
    commands = {
        "add": partial(_add_user_to_whitelist),
        "remove": partial(_remove_user_from_whitelist),
        "ban": partial(_add_user_to_blacklist),
        "unban": partial(_remove_user_from_blacklist)
    }
    try:
        command_name = command[0]
        if command_name in commands:
            return command[command_name](command, streamer, channel_id)
    except IndexError:
        LOGGER.error('Command missing arguments')
        return None
    except KeyError:
        LOGGER.error('Command missing')
        return None
    return None
