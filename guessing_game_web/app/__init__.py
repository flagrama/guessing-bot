from flask import Flask, redirect, url_for
from flask_login import LoginManager # pylint: disable=import-error
from flask_mongoengine import MongoEngine # pylint: disable=import-error
from guessing_game_web.config import app_config
from guessing_game_web.app import models

db = MongoEngine()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    try:
        return models.user.User.objects.get(streamer_id=user_id) #pylint: disable=no-member
    except models.user.User.DoesNotExist: #pylint: disable=no-member
        return models.user.User()

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('twitch.login'))

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "login.authorize"

    from guessing_game_web.app.twitch import twitch as twitch_blueprint
    app.register_blueprint(twitch_blueprint, url_prefix="/login")

    from guessing_game_web.app.home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from guessing_game_web.app.guessable import guessable as guessable_blueprint
    app.register_blueprint(guessable_blueprint, url_prefix="/dashboard/guessable")

    return app
