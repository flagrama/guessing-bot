from flask import redirect, url_for, flash
from flask_dance.consumer import oauth_authorized
from flask_login import login_user
from guessing_game_web.app.models.token import Token
from guessing_game_web.app.models.user import User
from guessing_game_bot.database import Streamer

from . import twitch

@twitch.route("/")
def start_authorize():
    return redirect(url_for("twitch.login"))

@twitch.route("/twitch/authorized")
@oauth_authorized.connect
def finish_authorize(blueprint, token):
    resp = blueprint.session.get("users")
    assert resp.ok, resp.text
    #Get/Create user
    streamer_id = resp.json()['data'][0]['id']
    username = resp.json()['data'][0]['display_name']
    email = resp.json()['data'][0]['email']
    try:
        user = getattr(User, 'objects').get(streamer_id=streamer_id)
        token = Token(provider="twitch", token=token)
        token.save()
        user.login_token = token
        user.save()
        token.user = user
        token.save()
    except User.DoesNotExist: #pylint: disable=no-member
        user = User(streamer_id=streamer_id, username=username, email=email)
        token = Token(provider="twitch", token=token)
        token.save()
        user.login_token = token
        user.save()
        token.user = user
        token.save()
    # Link to Guessing Game Bot Streamer
    try:
        streamer = Streamer.objects.get(channel_id=streamer_id) #pylint: disable=no-member
        user.streamer = streamer
        user.save()
        streamer.user = user
        streamer.save()
    except Streamer.DoesNotExist: #pylint: disable=no-member
        streamer = Streamer(name=username, channel_id=streamer_id, user=user)
        streamer.save()
        user.streamer = streamer
        user.save()
    # Login the user
    login_user(user)
    return redirect(url_for('home.dashboard'))
