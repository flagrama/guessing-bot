from database.command import *
from database.streamer import *

def add_command(streamer, name, output):
    message = ' '.join(output)
    new_command = Command(name = name, output = message)
    streamer.commands.append(new_command)
    streamer.save()

def remove_command(streamer, name):
    streamer.update(pull__commands__name = name)

def edit_command(streamer, name, output):
    message = ' '.join(output)
    Streamer.objects.filter(channel_id = streamer.channel_id, commands__name = name).update(set__commands__S__output = message)
    streamer.reload()
