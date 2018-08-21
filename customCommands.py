import mongoengine as mongodb
from database.command import *

def add_command(streamer, name, output):
    message = ' '.join(output)
    new_command = Command(name = name, output = message)
    streamer.commands.append(new_command)
    streamer.save()
