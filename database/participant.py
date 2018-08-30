import mongoengine as mongodb

class Participant(mongodb.EmbeddedDocument):
    username = mongodb.StringField(required=True)
    user_id = mongodb.IntField(required=True)
    session_points = mongodb.IntField()
    total_points = mongodb.IntField()
