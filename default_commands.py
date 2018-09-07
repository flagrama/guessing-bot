"""Contains the functions and classes of the bot's basic commands."""
from functools import partial
import custom_commands
import settings

def add_command(bot, command):
    """Adds a custom command to the database."""
    logger = settings.init_logger(__name__)
    logger.debug('Add Command command received')

    # Command exists
    if (command[1] in bot.commands['default']
            + bot.commands['guessing-game']):
        message = 'Command %s already exists' % command[1]
        logger.info(message)
        return message

    # New command is valid
    if len(command) > 2:
        message = 'Added custom command %s' % command[1]
        custom_commands.add_command(bot.streamer, command[1], command[2:])
        bot.commands['custom'] += [command[1]]
        logger.info('%s with output %s', message, ' '.join(command[2:]))
        logger.debug(bot.commands['custom'])
        return message

    # New command doesn't have output
    message = 'Custom commands require a message to send to chat when called'
    logger.info(message)
    return message

def delete_command(bot, command):
    """Deletes a custom command from the database."""
    logger = settings.init_logger(__name__)
    logger.debug('Delete Command command received')

    # Built-in command cannot be deleted
    if (command[1] in bot.commands['default']
            + bot.commands['guessing-game']):
        message = 'Command %s cannot be removed' % command[1]
        logger.info(message)
        return message

    # Command doesn't exist
    if not command[1] in bot.commands['custom']:
        message = 'Command %s does not exist' % command[1]
        logger.info(message)
        return message

    # Delete given command
    message = 'Removed custom command %s' % command[1]
    custom_commands.remove_command(bot.streamer, command[1])
    bot.commands['custom'].remove(command[1])
    logger.info(message)
    logger.debug(bot.commands['custom'])
    return message

def edit_command(bot, command):
    """Edits a custom command in the database."""
    logger = settings.init_logger(__name__)
    logger.debug('Edit Command command received')

    # Built-in commands cannot be edited
    if (command[1] in bot.commands['default']
            + bot.commands['guessing-game']):
        message = 'Command %s cannot be edited' % command[1]
        logger.info(message)
        return message

    # Command doesn't exist
    if not command[1] in bot.commands['custom']:
        message = 'Command %s does not exist' % command[1]
        logger.info(message)
        return message

    # Edited command is valid
    if len(command) > 2:
        message = 'Edited custom command %s' % command[1]
        custom_commands.edit_command(bot.streamer, command[1], command[2:])
        logger.info(message)
        logger.debug(bot.commands['custom'])
        return message

    # Edited command doesn't have output
    message = 'Custom commands require a message to send to chat when called'
    logger.info(message)
    return message

COMMANDS = {
    '!addcom': partial(add_command),
    '!delcom': partial(delete_command),
    '!editcom': partial(edit_command)
    }


def do_default_command(twitch_bot, command):
    """Calls the command function the user invokes."""
    logger = settings.init_logger(__name__)
    if len(command) < 2:
        message = 'Custom command name not provided'
        logger.info(message)
        return message

    try:
        return COMMANDS[command[0]](twitch_bot, command)
    except KeyError:
        message = 'Default command name not found'
        logger.error(message)
        return message
