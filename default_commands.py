import logging
import custom_commands
import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
if settings.DEBUG:
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)

def do_default_command(twitch_bot, command):
    try:
        command_name = command[0]
        custom_command_name = command[1]
    except IndexError:
        message = 'Custom command name not provided'
        LOGGER.error(message)
        return message

    if command_name == '!addcom':
        LOGGER.debug('Add Command command received')

        # Command exists
        if (custom_command_name in twitch_bot.commands['default']
                + twitch_bot.commands['guessing-game']):
            message = 'Command %s already exists' % custom_command_name
            LOGGER.info(message)
            return message

        # New command is valid
        if len(command) > 2:
            message = 'Added custom command %s' % custom_command_name
            custom_commands.add_command(twitch_bot.streamer, custom_command_name, command[2:])
            twitch_bot.commands['custom'] += [custom_command_name]
            LOGGER.info('%s with output %s', message, ' '.join(command[2:]))
            LOGGER.debug(twitch_bot.commands['custom'])
            return message

        # New command doesn't have output
        message = 'Custom commands require a message to send to chat when called'
        LOGGER.info(message)
        return message

    elif command_name == '!delcom':
        LOGGER.debug('Delete Command command received')

        # Built-in command cannot be deleted
        if (custom_command_name in twitch_bot.commands['default']
                + twitch_bot.commands['guessing-game']):
            message = 'Command %s cannot be removed' % custom_command_name
            LOGGER.info(message)
            return message

        # Command doesn't exist
        if not custom_command_name in twitch_bot.commands['custom']:
            message = 'Command %s does not exist' % custom_command_name
            LOGGER.info(message)
            return message

        # Delete given command
        message = 'Removed custom command %s' % custom_command_name
        custom_commands.remove_command(twitch_bot.streamer, custom_command_name)
        twitch_bot.commands['custom'].remove(custom_command_name)
        LOGGER.info(message)
        LOGGER.debug(twitch_bot.commands['custom'])
        return message

    elif command_name == '!editcom':
        LOGGER.debug('Edit Command command received')

        # Built-in commands cannot be edited
        if (custom_command_name in twitch_bot.commands['default']
                + twitch_bot.commands['guessing-game']):
            message = 'Command %s cannot be edited' % custom_command_name
            LOGGER.info(message)
            return message

        # Command doesn't exist
        if not custom_command_name in twitch_bot.commands['custom']:
            message = 'Command %s does not exist' % custom_command_name
            LOGGER.info(message)
            return message

        # Edited command is valid
        if len(command) > 2:
            message = 'Edited custom command %s' % custom_command_name
            custom_commands.edit_command(twitch_bot.streamer, custom_command_name, command[2:])
            LOGGER.info(message)
            LOGGER.debug(twitch_bot.commands['custom'])
            return message

        # Edited command doesn't have output
        message = 'Custom commands require a message to send to chat when called'
        LOGGER.info(message)
        return message
