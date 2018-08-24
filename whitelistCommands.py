import mongoengine as mongodb
from database.whitelist import WhitelistUser, BlacklistUser
from database.streamer import Streamer


# Currently will assume !hud <item> is the Guess Completion command
def do_whitelist_command(twitch_bot, connection, command):
    try:
        whitelist_command_name = command[1]
    except IndexError:
        twitch_bot.logger.error('Incomplete command')
        return

    if whitelist_command_name == 'reset':
        twitch_bot.logger.error('%s not implemented', whitelist_command_name)
        return
    elif whitelist_command_name == 'add':
        if add_user_to_whitelist(twitch_bot, command):
            message = 'User %s added to whitelist' % command[2]
            connection.privmsg(twitch_bot.channel, message)
            twitch_bot.logger.info(message)
            return
        else:
            connection.privmsg(twitch_bot.channel, 'Unable to add user to whitelist')
    elif whitelist_command_name == 'remove':
        if remove_user_from_whitelist(twitch_bot, command):
            message = 'User %s removed from whitelist' % command[2]
            connection.privmsg(twitch_bot.channel, message)
            twitch_bot.logger.info(message)
            return
        else:
            connection.privmsg(twitch_bot.channel, 'Unable to remove user from whitelist')
        return
    elif whitelist_command_name == 'ban':
        if add_user_to_blacklist(twitch_bot, command):
            message = 'User %s added to blacklist' % command[2]
            connection.privmsg(twitch_bot.channel, message)
            twitch_bot.logger.info(message)
            return
        else:
            connection.privmsg(twitch_bot.channel, 'Unable to add user to blacklist')
        return
    elif whitelist_command_name == 'unban':
        if remove_user_from_blacklist(twitch_bot, command):
            message = 'User %s removed from blacklist' % command[2]
            connection.privmsg(twitch_bot.channel, message)
            twitch_bot.logger.info(message)
            return
        else:
            connection.privmsg(twitch_bot.channel, 'Unable to remove user from blacklist')
        return
    else:
        item = command[2:]
        guess_completed(item)
        twitch_bot.logger.error('%s not implemented', whitelist_command_name)
        return


def get_username_from_command(command):
    try:
        username = command[2]
        return username
    except IndexError:
        return False


def add_user_to_whitelist(twitch_bot, command):
    username = get_username_from_command(command)

    if not username:
        twitch_bot.logger.error('Username not provided')
        return False

    new_user_id = twitch_bot.get_user_id(username)
    if not new_user_id:
        return False

    new_user = WhitelistUser(username = username, user_id = new_user_id)
    try:
        streamer = Streamer.objects.get(channel_id = twitch_bot.streamer.channel_id, whitelist__user_id = new_user_id) #pylint: disable=no-member
        if streamer.whitelist:
            twitch_bot.logger.info('User with ID %s already exists in the database' % new_user_id)
            return False
    except Streamer.DoesNotExist: #pylint: disable=no-member
        twitch_bot.logger.error('User with ID %s does not exist in the database' %new_user_id)

    try:
        twitch_bot.streamer.whitelist.append(new_user)
        twitch_bot.streamer.save()
        return True
    except mongodb.NotUniqueError:
        twitch_bot.logger.error('User with ID %s already exists in the database' % new_user_id)
    return False


def remove_user_from_whitelist(twitch_bot, command):
    username = get_username_from_command(command)

    if not username:
        twitch_bot.logger.error('Username not provided')
        return False

    existing_user_id = twitch_bot.get_user_id(username)
    if not existing_user_id:
        return False

    try:
        streamer = Streamer.objects.get(channel_id = twitch_bot.streamer.channel_id, whitelist__user_id = existing_user_id) #pylint: disable=no-member
        if not streamer.whitelist:
            return False
        Streamer.objects.update(channel_id = twitch_bot.streamer.channel_id, pull__whitelist__user_id = existing_user_id) #pylint: disable=no-member
        twitch_bot.streamer.save()
        return True
    except Streamer.DoesNotExist: #pylint: disable=no-member
        twitch_bot.logger.error('User with ID %s does not exist in the database' % existing_user_id)
        return False


def add_user_to_blacklist(twitch_bot, command):
    username = get_username_from_command(command)

    if not username:
        twitch_bot.logger.error('Username not provided')
        return False

    new_user_id = twitch_bot.get_user_id(username)
    if not new_user_id:
        return False

    new_user = BlacklistUser(username=username, user_id=new_user_id)
    try:
        streamer = Streamer.objects.get(channel_id = twitch_bot.streamer.channel_id, blacklist__user_id = new_user_id) #pylint: disable=no-member
        if streamer.blacklist:
            twitch_bot.logger.info('User with ID %s already exists in the database' % new_user_id)
            return False
    except Streamer.DoesNotExist: #pylint: disable=no-member
        twitch_bot.logger.error('User with ID %s does not exist in the database' % new_user_id)

    try:
        twitch_bot.streamer.blacklist.append(new_user)
        twitch_bot.streamer.save()
        return True
    except mongodb.NotUniqueError:
        twitch_bot.logger.error('User with ID %s already exists in the database' % new_user_id)
    return False


def remove_user_from_blacklist(twitch_bot, command):
    username = get_username_from_command(command)

    if not username:
        twitch_bot.logger.error('Username not provided')
        return False

    existing_user_id = twitch_bot.get_user_id(username)
    if not existing_user_id:
        return False

    try:
        streamer = Streamer.objects.get(channel_id = twitch_bot.streamer.channel_id, blacklist__user_id = existing_user_id) #pylint: disable=no-member
        if not streamer.whitelist:
            return False
        Streamer.objects.update(channel_id = twitch_bot.streamer.channel_id, pull__blacklist__user_id = existing_user_id) #pylint: disable=no-member
        twitch_bot.streamer.save()
        return True
    except Streamer.DoesNotExist: #pylint: disable=no-member
        twitch_bot.logger.error('User with ID %s does not exist in the database' % existing_user_id)
        return False


def guess_completed(item):
    return

