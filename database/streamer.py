import mongoengine as mongodb
from database.command import Command
from database.whitelist import WhitelistUser, BlacklistUser


class Streamer(mongodb.Document):
    name = mongodb.StringField(required = True)
    channel_id = mongodb.StringField(required = True, unique = True)
    commands = mongodb.ListField(mongodb.EmbeddedDocumentField(Command))
    # participants = mongodb.ListField(mongodb.EmbeddedDocumentField("Participant"))
    whitelist = mongodb.ListField(mongodb.EmbeddedDocumentField(WhitelistUser))
    blacklist = mongodb.ListField(mongodb.EmbeddedDocumentField(BlacklistUser))
    # session_log = mongodb.ListField(mongodb.EmbeddedDocumentField("SessionLogEntry"))
