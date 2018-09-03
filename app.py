import os.path
from flask import Flask, Blueprint
import flask_silk
from flask_autoindex import AutoIndexBlueprint
auto_bp = Blueprint('auto_bp', __name__)
AutoIndexBlueprint(auto_bp, browse_root=os.path.join(os.path.curdir, 'reports'))

app = Flask(__name__)
app.register_blueprint(auto_bp, url_prefix='/')

if __name__ == '__main__':
    app.run()
