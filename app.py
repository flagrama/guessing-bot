"""The webpage that displays all available run reports."""
import os
from flask import Flask, render_template

APP = Flask(__name__)
@APP.route('/')
def index():
    """Displays the index page."""
    return render_template('reports.html', bucket=os.environ['S3_BUCKET'])

if __name__ == '__main__':
    APP.run()
