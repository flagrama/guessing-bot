from flask import Blueprint

mode = Blueprint('mode', __name__)

from . import views