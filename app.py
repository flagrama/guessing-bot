import os.path
from flask import Flask
from flask_autoindex import AutoIndex

app = Flask(__name__)
AutoIndex(app, browse_root=os.path.join(os.path.curdir, 'reports'), add_url_rules=True)

if __name__ == '__main__':
    app.run()
