from guessing_game_web.app import db

class User(db.Document):
    streamer_id = db.IntField(required=True, unique=True) # pylint: disable=no-member
    username = db.StringField(required=True) # pylint: disable=no-member
    email = db.StringField(required=True) # pylint: disable=no-member
    modes = db.ListField(db.ReferenceField('Mode')) # pylint: disable=no-member
    guessables = db.ListField(db.ReferenceField('Guessable')) # pylint: disable=no-member
    streamer = db.ReferenceField('Streamer') # pylint: disable=no-member
    token = db.ReferenceField('Token') # pylint: disable=no-member

    def __repr__(self):
        return '<User %r>' % self.username
    def is_authenticated(self):
        if self.token:
            return True
        return False
    def is_active(self):
        return True
    def is_anonymous(self):
        if self.streamer_id:
            return False
        return True
    def get_id(self):
        return str(self.streamer_id)
    def get_id_int(self):
        return int(self.streamer_id)
    def get_name(self):
        return str(self.username)
