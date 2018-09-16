from datetime import datetime
from guessing_game_web.app import db

class Token(db.Document):
    provider = db.StringField()
    created_at = db.DateTimeField(default=datetime.utcnow)
    token = db.DictField()
    user = db.ReferenceField('User')
