from database.whitelist import *
from database.streamer import *

# Currently will assume !hud <item> is the Guess Completion command
def do_whitelist_command(twitch_bot, connection, command):
    try:
        whitelist_command_name = command[1]
    except IndexError:
        twitch_bot.logger.error('Incomplete command')
        return

    if(whitelist_command_name == 'reset'):
        twitch_bot.logger.error('%s not implemented', whitelist_command_name)
        return
    elif(whitelist_command_name == 'add'):
        if add_user_to_whitelist(twitch_bot, command):
            return
        else:
            connection.privmsg(twitch_bot.channel, 'Unable to add user to whitelist')
    elif(whitelist_command_name == 'remove'):
        twitch_bot.logger.error('%s not implemented', whitelist_command_name)
        return
    elif(whitelist_command_name == 'ban'):
        twitch_bot.logger.error('%s not implemented', whitelist_command_name)
        return
    elif(whitelist_command_name == 'unban'):
        twitch_bot.logger.error('%s not implemented', whitelist_command_name)
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
    new_user = WhitelistUser(username = username, user_id = new_user_id)
    try:
        twitch_bot.streamer.whitelist.append(new_user)
        twitch_bot.streamer.save()
        twitch_bot.logger.info('User %s added to whitelist' % username)
        return True
    except mongodb.NotUniqueError:
        twitch_bot.logger.error('User with ID %s already exists in the database' % new_user_id)
        return False

def guess_completed(item):
    return

