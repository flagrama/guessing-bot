from datetime import datetime
from guessing_game_web.app import db

class Token(db.Document):
    provider = db.StringField() # pylint: disable=no-member
    created_at = db.DateTimeField(default=datetime.utcnow) # pylint: disable=no-member
    token = db.DictField() # pylint: disable=no-member
    user = db.ReferenceField('User') # pylint: disable=no-member
