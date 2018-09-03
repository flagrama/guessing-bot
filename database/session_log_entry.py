import mongoengine as mongodb
import datetime

class SessionLogEntry(mongodb.EmbeddedDocument):
    timestamp = mongodb.DateTimeField(required=True, default=datetime.datetime.now())
    participant = mongodb.IntField(required=True)
    guess_type = mongodb.StringField(required=True, default='No Type')
    guess = mongodb.StringField(required=True)
    session_points = mongodb.IntField(required=True)
    total_points = mongodb.IntField(required=True)
