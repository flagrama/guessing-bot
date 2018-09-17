from flask import Blueprint

guessable = Blueprint('guessable', __name__)

from . import views
