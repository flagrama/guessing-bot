from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, validators
from guessing_game_web.app.models import guessable

class AddGuessable(FlaskForm):
    name = TextField('Guessable Item Name', validators=[validators.required()])
    codes = TextField('Guessing Codes', validators=[validators.required()])
    add = SubmitField('Add')

    def add_guessable(self, current_user, this_form):
        name = this_form.name.data
        codes = this_form.codes.data.split(',')
        this_guessable = guessable.Guessable(name=name, codes=codes).save()
        current_user.guessables.append(this_guessable)
        current_user.save()

class DeleteGuessable(FlaskForm):
    key = TextField('Guessable ID', validators=[validators.required()])
    name = TextField('Guessable Item Name', validators=[validators.required()])
    delete = SubmitField('Delete')

class UpdateGuessable(FlaskForm):
    key = TextField('Guessable ID', validators=[validators.required()])
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
