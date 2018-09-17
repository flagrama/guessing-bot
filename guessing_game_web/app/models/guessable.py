from guessing_game_web.app import db

class Guessable(db.Document):
    name = db.StringField(required=True) # pylint: disable=no-member
    codes = db.ListField(db.StringField(required=True), required=True) # pylint: disable=no-member

class Mode(db.Document):
    """The mode database class."""
    name = db.StringField(required=True) # pylint: disable=no-member
    items = db.ListField(db.StringField(required=True), required=True) # pylint: disable=no-member
