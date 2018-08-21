import mongoengine as mongodb

class Command(mongodb.EmbeddedDocument):
    name = mongodb.StringField(required = True)
    output = mongodb.StringField(required = True)
