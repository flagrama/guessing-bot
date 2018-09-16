from guessing_game_web.app import db

class User(db.Document):
    streamer_id = db.IntField(required=True, unique=True)
    username = db.StringField(required=True)
    email = db.StringField(required=True)
    token = db.ReferenceField('Token')

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
