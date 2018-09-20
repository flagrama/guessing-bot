import string
from flask import request, flash, render_template, redirect, url_for
from flask_login import login_required, current_user
from guessing_game_web.app import db
from guessing_game_web.app.models import form, user, guessable as db_openguess
from guessing_game_web.app.openguess import views as openguess_view
from . import openguess

def get_user_openguess(openguess_id):
    try:
        user_openguess = getattr(user.User, 'objects')(
            username=current_user.username, openguesses__contains=openguess_id)
    except (getattr(user.User, 'DoesNotExist'), getattr(db, 'ValidationError')):
        flash("Access Violation!", 'danger')
        return None
    return user_openguess

def get_openguess(openguess_id):
    get_user_openguess(openguess_id)
    try:
        this_openguess = getattr(db_openguess.OpenGuess, 'objects').get(id=openguess_id)
    except (getattr(user.User, 'DoesNotExist'), getattr(db, 'ValidationError')):
        flash("Access Violation!", 'danger')
        return None
    return this_openguess

def __add_openguess(this_form):
    pass

def __update_openguess(this_form):
    pass

def __delete_openguess(openguess_id):
    pass

@openguess.route('add', methods=['GET', 'POST'])
@login_required
def add():
    this_form = form.AddOpenGuess()

    if request.method == 'POST':
        success = True
        if this_form.validate():
            result = __add_openguess(this_form)
            if isinstance(result, list) and not isinstance(result, str):
                for message in result:
                    flash(message, 'danger')
                    success = False
            elif isinstance(result, str):
                flash(result, 'danger')
                success = False
            if success:
                flash("Created {0}".format(this_form.name.data.lower()), 'success')
                return redirect(url_for('home.dashboard'))
        else:
            flash('All fields are required', 'danger')

    return render_template('openguess/add.html', title="Add Open Guess", form=this_form)

@openguess.route('update/<openguess_id>', methods=['GET', 'POST'])
@login_required
def update(openguess_id):
    this_form = form.UpdateOpenGuess()

    if request.method == 'POST':
        success = True
        if this_form.validate():
            result = __update_openguess(this_form)
            if isinstance(result, list) and not isinstance(result, str):
                for message in result:
                    flash(message, 'danger')
                    success = False
            elif isinstance(result, str):
                flash(result, 'danger')
                success = False
            if success:
                flash("Updated {0}".format(this_form.name.data.lower()), 'success')
                return redirect(url_for('home.dashboard'))
        else:
            flash('All fields are required', 'danger')

    this_openguess = get_openguess(openguess_id)
    if not this_openguess:
        return redirect(url_for('home.dashboard'))
    return render_template(
        'openguess/update.html',
        title="Update {0}".format(this_openguess.name),
        existing_key=this_openguess.id,
        existing_name=this_openguess.name,
        existing_guessables=','.join(this_openguess.guessables),
        form=this_form)

@openguess.route('delete/<openguess_id>', methods=['GET'])
@login_required
def delete(openguess_id):
    result = __delete_openguess(openguess_id)
    if not result:
        return redirect(url_for('home.dashboard'))
    flash("Deleted {0}".format(result), 'success')
    return redirect(url_for('home.dashboard'))