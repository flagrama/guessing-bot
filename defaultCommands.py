import customCommands

def do_default_command(twitch_bot, connection, command):
        if command[0] == '!addcom':
            twitch_bot.logger.debug('Add Command command received')

            # Command exists
            if command[1] in twitch_bot.commands:
                message = 'Command %s already exists' % command[1]
                twitch_bot.logger.info(message)
                connection.privmsg(twitch_bot.channel, message)

            # New command is valid
            elif len(command) > 2:
                message = 'Added custom command %s' % command[1]
                customCommands.add_command(twitch_bot.streamer, command[1], command[2:])
                twitch_bot.commands += [command[1]]
                twitch_bot.logger.info(message + ' with output %s' % ' '.join(command[2:]))
                connection.privmsg(twitch_bot.channel, message)
                twitch_bot.logger.debug(twitch_bot.commands)

            # New command doesn't have output
            else:
                message = 'Custom commands require a message to send to chat when called'
                twitch_bot.logger.info(message)
                connection.privmsg(twitch_bot.channel, message)

        elif command[0] == '!delcom':
            twitch_bot.logger.debug('Delete Command command received')

            # Built-in command cannot be deleted
            if command[1] in twitch_bot.default_commands:
                message = 'Command %s cannot be removed' % command[1]
                twitch_bot.logger.info(message)
                connection.privmsg(twitch_bot.channel, message)

            # Command doesn't exist
            elif not command[1] in twitch_bot.commands:
                message = 'Command %s does not exist' % command[1]
                twitch_bot.logger.info(message)
                connection.privmsg(twitch_bot.channel, message)

            # Delete given command
            else:
                message = 'Removed custom command %s' % command[1]
                customCommands.remove_command(twitch_bot.streamer, command[1])
                twitch_bot.commands.remove(command[1])
                twitch_bot.logger.info(message)
                connection.privmsg(twitch_bot.channel, message)
                twitch_bot.logger.debug(twitch_bot.commands)

        elif command[0] == '!editcom':
            twitch_bot.logger.debug('Edit Command command received')

            # Built-in commands cannot be edited
            if command[1] in twitch_bot.default_commands:
                message = 'Command %s cannot be edited' % command[1]
                twitch_bot.logger.info(message)
                connection.privmsg(twitch_bot.channel, message)

            # Command doesn't exist
            elif not command[1] in twitch_bot.commands:
                message = 'Command %s does not exist' % command[1]
                twitch_bot.logger.info(message)
                connection.privmsg(twitch_bot.channel, message)

            # Edit given command
            else:
                message = 'Edited custom command %s' % command[1]
                customCommands.edit_command(twitch_bot.streamer, command[1], command[2:])
                twitch_bot.logger.info(message)
                connection.privmsg(twitch_bot.channel, message)
                twitch_bot.logger.debug(twitch_bot.commands)
