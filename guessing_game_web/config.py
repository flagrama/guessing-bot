import os

class Config(object):
    """
    Common configurations
    """
    TWITCH_OAUTH_CLIENT_ID = os.environ.get("TWITCH_ID")
    TWITCH_OAUTH_CLIENT_SECRET = os.environ.get("TWITCH_SECRET")
    SECRET_KEY = os.environ.get("FLASK_SECRET")
    MONGODB_URI = os.environ.get("MONGODB_URI")


class DevelopmentConfig(Config):
    """
    Development configurations
    """
    DEBUG = True


class ProductionConfig(Config):
    """
    Production configurations
    """
    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
