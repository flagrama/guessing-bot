"""Stores functions for managing custom commands."""
from .database import Command

def add_command(streamer, name, output):
    """Adds a custom command to the database."""
    message = ' '.join(output)
    new_command = Command(name=name, output=message)
    streamer.commands.append(new_command)
    streamer.save()

def remove_command(streamer, name):
    """Removes a custom command from the database."""
    streamer.update(pull__commands__name=name)
    streamer.save()

def edit_command(streamer, name, output):
    """Edits a custom command in the database."""
    message = ' '.join(output)
    for command in streamer.commands:
        if command.name == name:
            command.output = message
    streamer.save()
