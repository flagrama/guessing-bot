"""Stores the mongoengine database classes."""
import datetime
import mongoengine

class Command(mongoengine.EmbeddedDocument):
    """The custom command database class."""
    name = mongoengine.StringField(required=True)
    output = mongoengine.StringField(required=True)

class Mode(mongoengine.EmbeddedDocument):
    """The mode database class."""
    name = mongoengine.StringField(required=True)
    items = mongoengine.ListField(mongoengine.StringField())

class Participant(mongoengine.EmbeddedDocument):
    """The participant database class."""
    username = mongoengine.StringField(required=True)
    user_id = mongoengine.IntField(required=True)
    session_points = mongoengine.IntField()
    total_points = mongoengine.IntField()

class SessionLogEntry(mongoengine.EmbeddedDocument):
    """The session log entry database class."""
    timestamp = mongoengine.DateTimeField(required=True, default=datetime.datetime.now())
    participant = mongoengine.IntField(required=True)
    participant_name = mongoengine.StringField(required=True)
    guess_type = mongoengine.StringField(required=True, default='No Type')
    guess = mongoengine.StringField(required=True)
    session_points = mongoengine.IntField(required=True)
    total_points = mongoengine.IntField(required=True)

class Session(mongoengine.EmbeddedDocument):
    """The session database class."""
    guesses = mongoengine.ListField(mongoengine.EmbeddedDocumentField(SessionLogEntry))

class WhitelistUser(mongoengine.EmbeddedDocument):
    """The whitelist user database class."""
    username = mongoengine.StringField(required=True)
    user_id = mongoengine.IntField(required=True)


class BlacklistUser(mongoengine.EmbeddedDocument):
    """The blacklist user database class."""
    username = mongoengine.StringField(required=True)
    user_id = mongoengine.IntField(required=True)

class DbStreamer(mongoengine.Document):
    """The streamer database class."""
    name = mongoengine.StringField(required=True)
    channel_id = mongoengine.StringField(required=True, unique=True)
    first_bonus = mongoengine.IntField(default=1)
    points = mongoengine.IntField(default=1)
    commands = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Command))
    participants = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Participant))
    whitelist = mongoengine.ListField(mongoengine.EmbeddedDocumentField(WhitelistUser))
    blacklist = mongoengine.ListField(mongoengine.EmbeddedDocumentField(BlacklistUser))
    sessions = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Session))
    multi_guess = mongoengine.DictField()
    guessables = mongoengine.DictField()
    modes = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Mode))

    meta = {"collection":"streamer"}
