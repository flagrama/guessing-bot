from distutils.core import setup # pylint: disable=no-name-in-module,import-error

setup(
    name='GuessingGameBot',
    version='1.1-dev',
    packages=['guessing_game_bot', 'guessing_game_web'],
    install_requires=[
        "requests==2.18.4",
        "boto3==1.9.0",
        "Flask==1.0.2",
        "Flask_Dance==1.1.0",
        "Flask_Login==0.4.1",
        "flask_mongoengine==0.9.5",
        "irc==16.4",
        "mongoengine==0.15.3",
        "gunicorn==19.9.0",
        "blinker==1.4"
    ]
)
