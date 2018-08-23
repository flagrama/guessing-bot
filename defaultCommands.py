import customCommands

def do_default_command(twitch_bot, connection, command):
    try:
        command_name = command[0]
        custom_command_name = command[1]
    except IndexError:
        message = 'Custom command name not provided'
        twitch_bot.logger.error(message)
        connection.privmsg(twitch_bot.channel, message)
        return

    if command_name == '!addcom':
        twitch_bot.logger.debug('Add Command command received')

        # Command exists
        if custom_command_name in twitch_bot.commands:
            message = 'Command %s already exists' % custom_command_name
            twitch_bot.logger.info(message)
            connection.privmsg(twitch_bot.channel, message)

        # New command is valid
        elif len(command) > 2:
            message = 'Added custom command %s' % custom_command_name
            customCommands.add_command(twitch_bot.streamer, custom_command_name, command[2:])
            twitch_bot.commands += [custom_command_name]
            twitch_bot.logger.info(message + ' with output %s' % ' '.join(command[2:]))
            connection.privmsg(twitch_bot.channel, message)
            twitch_bot.logger.debug(twitch_bot.commands)

        # New command doesn't have output
        else:
            message = 'Custom commands require a message to send to chat when called'
            twitch_bot.logger.info(message)
            connection.privmsg(twitch_bot.channel, message)

    elif command_name == '!delcom':
        twitch_bot.logger.debug('Delete Command command received')

        # Built-in command cannot be deleted
        if custom_command_name in twitch_bot.default_commands:
            message = 'Command %s cannot be removed' % custom_command_name
            twitch_bot.logger.info(message)
            connection.privmsg(twitch_bot.channel, message)

        # Command doesn't exist
        elif not custom_command_name in twitch_bot.commands:
            message = 'Command %s does not exist' % custom_command_name
            twitch_bot.logger.info(message)
            connection.privmsg(twitch_bot.channel, message)

        # Delete given command
        else:
            message = 'Removed custom command %s' % custom_command_name
            customCommands.remove_command(twitch_bot.streamer, custom_command_name)
            twitch_bot.commands.remove(custom_command_name)
            twitch_bot.logger.info(message)
            connection.privmsg(twitch_bot.channel, message)
            twitch_bot.logger.debug(twitch_bot.commands)

    elif command_name == '!editcom':
        twitch_bot.logger.debug('Edit Command command received')

        # Built-in commands cannot be edited
        if custom_command_name in twitch_bot.default_commands:
            message = 'Command %s cannot be edited' % custom_command_name
            twitch_bot.logger.info(message)
            connection.privmsg(twitch_bot.channel, message)

        # Command doesn't exist
        elif not custom_command_name in twitch_bot.commands:
            message = 'Command %s does not exist' % custom_command_name
            twitch_bot.logger.info(message)
            connection.privmsg(twitch_bot.channel, message)



        # Edited command is valid
        elif len(command) > 2:
            message = 'Edited custom command %s' % custom_command_name
            customCommands.edit_command(twitch_bot.streamer, custom_command_name, command[2:])
            twitch_bot.logger.info(message)
            connection.privmsg(twitch_bot.channel, message)
            twitch_bot.logger.debug(twitch_bot.commands)

        # Edited command doesn't have output
        else:
            message = 'Custom commands require a message to send to chat when called'
            twitch_bot.logger.info(message)
            connection.privmsg(twitch_bot.channel, message)
