import mongoengine as mongodb
from database.command import Command
from database.whitelist import WhitelistUser, BlacklistUser
from database.participant import Participant
from database.session import Session


class Streamer(mongodb.Document):
    name = mongodb.StringField(required=True)
    channel_id = mongodb.StringField(required=True, unique=True)
    first_bonus = mongodb.IntField(default=1)
    points = mongodb.IntField(default=1)
    commands = mongodb.ListField(mongodb.EmbeddedDocumentField(Command))
    participants = mongodb.ListField(mongodb.EmbeddedDocumentField(Participant))
    whitelist = mongodb.ListField(mongodb.EmbeddedDocumentField(WhitelistUser))
    blacklist = mongodb.ListField(mongodb.EmbeddedDocumentField(BlacklistUser))
    sessions = mongodb.ListField(mongodb.EmbeddedDocumentField(Session))
