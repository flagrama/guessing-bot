from guessing_game_web.app import db

class Guessable(db.Document):
    name = db.StringField(required=True)
    codes = db.ListField(db.StringField(required=True), required=True)

class Mode(db.Document):
    """The mode database class."""
    name = db.StringField(required=True)
    items = db.ListField(db.StringField(required=True), required=True)
