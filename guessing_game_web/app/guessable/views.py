from flask import request, flash, render_template, redirect, url_for
from flask_login import login_required, current_user # pylint: disable=import-error
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from guessing_game_web.app.models import form
from . import guessable

@guessable.route('add', methods=['GET', 'POST'])
@login_required
def add():
    this_form = form.AddGuessable()

    if request.method == 'POST':
        if this_form.validate():
            form.AddGuessable.add_guessable(current_user, this_form)
            flash("Successfully created Guessable", 'success')
            return redirect(url_for('home.dashboard'))
        flash('All fields are required', 'danger')

    return render_template('guessable/add.html', title="Add Guessable", form=this_form)
