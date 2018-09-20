from guessing_game_web.app import db

class Guessable(db.Document):
    name = getattr(db, 'StringField')(required=True)
    codes = getattr(db, 'ListField')(getattr(db, 'StringField')(required=True), required=True)

class Mode(db.Document):
    """The mode database class."""
    name = getattr(db, 'StringField')(required=True)
    guessables = getattr(db, 'ListField')(getattr(db, 'StringField')(required=True), required=True)

class OpenGuess(db.Document):
    name = db.StringField(required=True) # pylint: disable=no-member
    guessables = db.ListField(db.ReferenceField(Guessable), required=True) # pylint: disable=no-member
    locations = db.ListField(db.ReferenceField(Guessable), required=True) # pylint: disable=no-member
