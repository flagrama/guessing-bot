from datetime import datetime
from guessing_game_web.app import db

class Token(db.Document):
    provider = getattr(db, 'StringField')()
    created_at = getattr(db, 'DateTimeField')(default=datetime.utcnow)
    token = getattr(db, 'DictField')()
    user = getattr(db, 'ReferenceField')('User')
