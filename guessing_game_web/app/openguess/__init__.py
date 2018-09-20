from flask import Blueprint

openguess = Blueprint('openguess', __name__)

from . import views