import mongoengine as mongodb

class Streamer(mongodb.Document):
    name = mongodb.StringField(required = True)
    twitch_id = mongodb.StringField(required = True)
    commands = mongodb.ListField(mongodb.EmbeddedDocumentField("Command"))
    participants = mongodb.ListField(mongodb.EmbeddedDocumentField("Participant"))
    whitelist = mongodb.ListField(mongodb.EmbeddedDocumentField("WhitelistUser"))
    session_log = mongodb.ListField(mongodb.EmbeddedDocumentField("SessionLogEntry"))
