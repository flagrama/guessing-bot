"""Contains the functions and classes of the bot's basic commands."""
import logging
from functools import partial
import custom_commands
import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
if settings.DEBUG:
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)

def add_command(bot, command):
    """Adds a custom command to the database."""
    LOGGER.debug('Add Command command received')

    # Command exists
    if (command[1] in bot.commands['default']
            + bot.commands['guessing-game']):
        message = 'Command %s already exists' % command[1]
        LOGGER.info(message)
        return message

    # New command is valid
    if len(command) > 2:
        message = 'Added custom command %s' % command[1]
        custom_commands.add_command(bot.streamer, command[1], command[2:])
        bot.commands['custom'] += [command[1]]
        LOGGER.info('%s with output %s', message, ' '.join(command[2:]))
        LOGGER.debug(bot.commands['custom'])
        return message

    # New command doesn't have output
    message = 'Custom commands require a message to send to chat when called'
    LOGGER.info(message)
    return message

def delete_command(bot, command):
    """Deletes a custom command from the database."""
    LOGGER.debug('Delete Command command received')

    # Built-in command cannot be deleted
    if (command[1] in bot.commands['default']
            + bot.commands['guessing-game']):
        message = 'Command %s cannot be removed' % command[1]
        LOGGER.info(message)
        return message

    # Command doesn't exist
    if not command[1] in bot.commands['custom']:
        message = 'Command %s does not exist' % command[1]
        LOGGER.info(message)
        return message

    # Delete given command
    message = 'Removed custom command %s' % command[1]
    custom_commands.remove_command(bot.streamer, command[1])
    bot.commands['custom'].remove(command[1])
    LOGGER.info(message)
    LOGGER.debug(bot.commands['custom'])
    return message

def edit_command(bot, command):
    """Edits a custom command in the database."""
    LOGGER.debug('Edit Command command received')

    # Built-in commands cannot be edited
    if (command[1] in bot.commands['default']
            + bot.commands['guessing-game']):
        message = 'Command %s cannot be edited' % command[1]
        LOGGER.info(message)
        return message

    # Command doesn't exist
    if not command[1] in bot.commands['custom']:
        message = 'Command %s does not exist' % command[1]
        LOGGER.info(message)
        return message

    # Edited command is valid
    if len(command) > 2:
        message = 'Edited custom command %s' % command[1]
        custom_commands.edit_command(bot.streamer, command[1], command[2:])
        LOGGER.info(message)
        LOGGER.debug(bot.commands['custom'])
        return message

    # Edited command doesn't have output
    message = 'Custom commands require a message to send to chat when called'
    LOGGER.info(message)
    return message

COMMANDS = {
    '!addcom': partial(add_command),
    '!delcom': partial(delete_command),
    '!editcom': partial(edit_command)
    }


def do_default_command(twitch_bot, command):
    """Calls the command function the user invokes."""
    if len(command) < 2:
        message = 'Custom command name not provided'
        LOGGER.info(message)
        return message

    try:
        return COMMANDS[command[0]](twitch_bot, command)
    except KeyError:
        message = 'Default command name not found'
        LOGGER.error(message)
        return message
