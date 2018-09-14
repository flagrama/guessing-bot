"""Contains the functions and classes of the bot's basic commands."""
from functools import partial
from . import custom_commands
from . import settings

def add_command(streamer, existing_commands, command, output):
    """Adds a custom command to the database."""
    logger = settings.init_logger(__name__)
    logger.debug('Add Command command received')

    # Command exists
    if (command in existing_commands['default']
            + existing_commands['guessing-game']):
        message = 'Command %s already exists' % command
        logger.info(message)
        return existing_commands['custom'], message

    # New command is valid
    if output:
        message = 'Added custom command %s' % command
        custom_commands.add_command(streamer, command, output)
        existing_commands['custom'] += [command]
        logger.info('%s with output %s', message, ' '.join(output))
        logger.debug(existing_commands['custom'])
        return existing_commands['custom'], message

    # New command doesn't have output
    message = 'Custom commands require a message to send to chat when called'
    logger.info(message)
    return existing_commands['custom'], message

def delete_command(streamer, existing_commands, command, output):
    """Deletes a custom command from the database."""
    logger = settings.init_logger(__name__)
    logger.debug('Delete Command command received')

    if output:
        message = 'Delete command does not take an output'
        logger.info(message)
        return existing_commands['custom'], message

    # Built-in command cannot be deleted
    if (command in existing_commands['default']
            + existing_commands['guessing-game']):
        message = 'Command %s cannot be removed' % command
        logger.info(message)
        return existing_commands['custom'], message

    # Command doesn't exist
    if not command in existing_commands['custom']:
        message = 'Command %s does not exist' % command
        logger.info(message)
        return existing_commands['custom'], message

    # Delete given command
    message = 'Removed custom command %s' % command
    custom_commands.remove_command(streamer, command)
    existing_commands['custom'].remove(command)
    logger.info(message)
    logger.debug(existing_commands['custom'])
    return existing_commands['custom'], message

def edit_command(streamer, existing_commands, command, output):
    """Edits a custom command in the database."""
    logger = settings.init_logger(__name__)
    logger.debug('Edit Command command received')

    # Built-in commands cannot be edited
    if (command in existing_commands['default']
            + existing_commands['guessing-game']):
        message = 'Command %s cannot be edited' % command
        logger.info(message)
        return existing_commands['custom'], message

    # Command doesn't exist
    if not command in existing_commands['custom']:
        message = 'Command %s does not exist' % command
        logger.info(message)
        return existing_commands['custom'], message

    # Edited command is valid
    if output:
        message = 'Edited custom command %s' % command
        custom_commands.edit_command(streamer, command, output)
        logger.info(message)
        logger.debug(existing_commands['custom'])
        return existing_commands['custom'], message

    # Edited command doesn't have output
    message = 'Custom commands require a message to send to chat when called'
    logger.info(message)
    return existing_commands['custom'], message

COMMANDS = {
    '!addcom': partial(add_command),
    '!delcom': partial(delete_command),
    '!editcom': partial(edit_command)
    }

def do_default_command(streamer, existing_commands, command, value):
    """Calls the command function the user invokes."""
    logger = settings.init_logger(__name__)
    if not value:
        message = 'Custom command name not provided'
        logger.info(message)
        return existing_commands['custom'], message
    try:
        custom_command_name = value[0]
        if len(value) > 1:
            custom_command_output = value[1:]
        else:
            custom_command_output = None
        return COMMANDS[command](
            streamer, existing_commands, custom_command_name, custom_command_output)
    except KeyError:
        message = 'Default command name not found'
        logger.error(message)
        return existing_commands['custom'], message
