from database import Command, Streamer

def add_command(streamer, name, output):
    message = ' '.join(output)
    new_command = Command(name=name, output=message)
    streamer.commands.append(new_command)
    streamer.save()
    streamer.reload()

def remove_command(streamer, name):
    streamer.update(pull__commands__name=name)
    streamer.reload()

def edit_command(streamer, name, output):
    message = ' '.join(output)
    Streamer.objects.filter( #pylint: disable=no-member
        channel_id=streamer.channel_id, commands__name=name).update(
            set__commands__S__output=message)
    streamer.reload()
