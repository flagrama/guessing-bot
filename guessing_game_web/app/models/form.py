from flask_wtf import FlaskForm
from wtforms import TextField, FieldList, FormField, SubmitField, validators
from wtforms import Form as NoCsrfForm

class AddGuessable(FlaskForm):
    name = TextField('Guessable Item Name', validators=[validators.required()])
    codes = TextField('Guessing Codes', validators=[validators.required()])
    add = SubmitField('Add')

class UpdateGuessable(FlaskForm):
    key = TextField('Guessable ID')
    name = TextField('Guessable Item Name', validators=[validators.required()])
    codes = TextField('Guessing Codes', validators=[validators.required()])
    update = SubmitField('Update')

class AddMode(FlaskForm):
    name = TextField('Mode Name', validators=[validators.required()])
    guessables = TextField('Mode Guessable Item Names', validators=[validators.required()])
    add = SubmitField('Add')

class UpdateMode(FlaskForm):
    key = TextField('Guessable ID', validators=[validators.required()])
    name = TextField('Mode Name', validators=[validators.required()])
    guessables = TextField('Mode Guessable Item Names', validators=[validators.required()])
    update = SubmitField('Update')

class OpenGuessGuessable(NoCsrfForm):
    guessable_name = TextField('Name')
    codes = TextField('Codes')

class AddOpenGuess(FlaskForm):
    name = TextField('Open Guess Name', validators=[validators.required()])
    guessables = FieldList(
        FormField(
            OpenGuessGuessable, default=OpenGuessGuessable()),
        min_entries=1, label='Guessables')
    locations = FieldList(
        FormField(
            OpenGuessGuessable, default=OpenGuessGuessable()),
        min_entries=1, label='Locations')
    add = SubmitField('Add')

class UpdateOpenGuess(FlaskForm):
    key = TextField('Guessable ID', validators=[validators.required()])
    name = TextField('Open Guess Name', validators=[validators.required()])
    guessables = FieldList(
        FormField(
            OpenGuessGuessable, default=OpenGuessGuessable()),
        min_entries=1, label='Guessables')
    locations = FieldList(
        FormField(
            OpenGuessGuessable, default=OpenGuessGuessable()),
        min_entries=1, label='Locations')
    update = SubmitField('Update')
