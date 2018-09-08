"""Stores functions for managing custom commands."""
from database import Command, DbStreamer

def add_command(streamer, name, output):
    """Adds a custom command to the database."""
    message = ' '.join(output)
    new_command = Command(name=name, output=message)
    streamer.commands.append(new_command)
    streamer.save()
    streamer.reload()

def remove_command(streamer, name):
    """Removes a custom command from the database."""
    streamer.update(pull__commands__name=name)
    streamer.reload()

def edit_command(streamer, name, output):
    """Edits a custom command in the database."""
    message = ' '.join(output)
    DbStreamer.objects.filter( #pylint: disable=no-member
        channel_id=streamer.channel_id, commands__name=name).update(
            set__commands__S__output=message)
    streamer.reload()
