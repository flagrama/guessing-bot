from flask import Blueprint
from flask_dance import OAuth2ConsumerBlueprint # pylint: disable=import-error

twitch = OAuth2ConsumerBlueprint(
    "twitch", __name__,
    base_url="https://api.twitch.tv/helix/",
    token_url="https://id.twitch.tv/oauth2/token",
    authorization_url="https://id.twitch.tv/oauth2/authorize",
    redirect_uri='http://localhost:8000/login/twitch/authorized',
    scope=('user:read:email')
)
twitch.from_config["client_id"] = "TWITCH_OAUTH_CLIENT_ID"
twitch.from_config["client_secret"] = "TWITCH_OAUTH_CLIENT_SECRET"

from . import views
