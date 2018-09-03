import datetime
import mongoengine

class Command(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
    output = mongoengine.StringField(required=True)

class Participant(mongoengine.EmbeddedDocument):
    username = mongoengine.StringField(required=True)
    user_id = mongoengine.IntField(required=True)
    session_points = mongoengine.IntField()
    total_points = mongoengine.IntField()

class SessionLogEntry(mongoengine.EmbeddedDocument):
    timestamp = mongoengine.DateTimeField(required=True, default=datetime.datetime.now())
    participant = mongoengine.IntField(required=True)
    participant_name = mongoengine.StringField(required=True)
    guess_type = mongoengine.StringField(required=True, default='No Type')
    guess = mongoengine.StringField(required=True)
    session_points = mongoengine.IntField(required=True)
    total_points = mongoengine.IntField(required=True)

class Session(mongoengine.EmbeddedDocument):
    guesses = mongoengine.ListField(mongoengine.EmbeddedDocumentField(SessionLogEntry))

class WhitelistUser(mongoengine.EmbeddedDocument):
    username = mongoengine.StringField(required=True)
    user_id = mongoengine.IntField(required=True)


class BlacklistUser(mongoengine.EmbeddedDocument):
    username = mongoengine.StringField(required=True)
    user_id = mongoengine.IntField(required=True)

class Streamer(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    channel_id = mongoengine.StringField(required=True, unique=True)
    first_bonus = mongoengine.IntField(default=1)
    points = mongoengine.IntField(default=1)
    commands = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Command))
    participants = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Participant))
    whitelist = mongoengine.ListField(mongoengine.EmbeddedDocumentField(WhitelistUser))
    blacklist = mongoengine.ListField(mongoengine.EmbeddedDocumentField(BlacklistUser))
    sessions = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Session))
