import mongoengine as mongodb
from database.session_log_entry import SessionLogEntry

class Session(mongodb.EmbeddedDocument):
    guesses = mongodb.ListField(mongodb.EmbeddedDocumentField(SessionLogEntry))
