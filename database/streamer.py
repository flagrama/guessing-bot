import mongoengine as mongodb
import database.command
import database.whitelist

class Streamer(mongodb.Document):
    name = mongodb.StringField(required = True)
    channel_id = mongodb.StringField(required = True, unique = True)
    commands = mongodb.ListField(mongodb.EmbeddedDocumentField("Command"))
    # participants = mongodb.ListField(mongodb.EmbeddedDocumentField("Participant"))
    whitelist = mongodb.ListField(mongodb.EmbeddedDocumentField("WhitelistUser"))
    # session_log = mongodb.ListField(mongodb.EmbeddedDocumentField("SessionLogEntry"))
