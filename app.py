import os
import boto3
from flask import Flask, render_template
from flask_autoindex import AutoIndex

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('reports.html', bucket=os.environ['S3_BUCKET'])

if __name__ == '__main__':
    app.run()
