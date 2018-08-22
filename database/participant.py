import mongoengine as mongodb

class Participant(mongodb.EmbeddedDocument):
    username = mongodb.StringField(required = True)
    session_points = mongodb.IntField()
    total_points = mongodb.IntField()
