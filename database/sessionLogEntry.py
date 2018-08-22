import mongoengine as mongodb
import datetime

class SessionLogEntry(mongodb.EmbeddedDocument):
    timestamp = mongodb.DateTimeField(required = True, default = datetime.datetime.now())
    username = mongodb.StringField(required = True)
    guess = mongodb.StringField(required = True)
    session_points = mongodb.IntField(required = True)
