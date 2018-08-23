import mongoengine as mongodb

class WhitelistUser(mongodb.EmbeddedDocument):
    username = mongodb.StringField(required = True)
    user_id = mongodb.IntField(required = True, unique = True)
