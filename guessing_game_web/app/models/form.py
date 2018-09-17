from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, validators

class AddGuessable(FlaskForm):
    name = TextField('Guessable Item Name', validators=[validators.required()])
    codes = TextField('Guessing Codes', validators=[validators.required()])
    add = SubmitField('Add')

class DeleteGuessable(FlaskForm):
    key = TextField('Guessable ID', validators=[validators.required()])
    name = TextField('Guessable Item Name', validators=[validators.required()])
    delete = SubmitField('Delete')

class UpdateGuessable(FlaskForm):
    key = TextField('Guessable ID')
    name = TextField('Guessable Item Name', validators=[validators.required()])
    codes = TextField('Guessing Codes', validators=[validators.required()])
    update = SubmitField('Update')

class ResetGuessable(FlaskForm):
    reset = SubmitField('Reset')

class AddMode(FlaskForm):
    name = TextField('Mode Name', validators=[validators.required()])
    guessables = TextField('Mode Guessable Item Names', validators=[validators.required()])
    add = SubmitField('Add')

class DeleteMode(FlaskForm):
    key = TextField('Guessable ID', validators=[validators.required()])
    name = TextField('Mode Name', validators=[validators.required()])
    delete = SubmitField('Delete')

class UpdateMode(FlaskForm):
    key = TextField('Guessable ID', validators=[validators.required()])
    guessables = TextField('Mode Guessable Item Names', validators=[validators.required()])
    update = SubmitField('Update')

class ResetMode(FlaskForm):
    reset = SubmitField('Reset')
