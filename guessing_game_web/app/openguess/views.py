import string
from flask import request, flash, render_template, redirect, url_for
from flask_login import login_required, current_user
from guessing_game_web.app import db
from guessing_game_web.app.models import exception, form, user, guessable as db_openguess
from guessing_game_web.app.openguess import views as openguess_view
from . import openguess

def get_openguess(openguess_id):
    if not getattr(user.User, 'objects')(
            username=current_user.username, open_guesses__contains=openguess_id):
        raise exception.UserAccessException
    this_openguess = getattr(db_openguess.OpenGuess, 'objects').get(id=openguess_id)
    return this_openguess

def __add_openguess(this_form):
    pass
    # name = this_form.name.data.lower()
    # guessables = this_form.guessables.data.split(',')
    # guessables = list(set(string.capwords(i) for i in guessables))
    # matches = []
    # not_found = []
    # for this_mode in current_user.modes:
    #     if string.capwords(this_mode.name) == string.capwords(name):
    #         return "Mode name {0} already exists".format(string.capwords(name))
    #     item_matches = set(this_mode.guessables).intersection(set(guessables))
    #     if item_matches:
    #         matches += ["Mode item(s) {0} already exists in {1}".format(
    #             ', '.join(item_matches), string.capwords(this_mode.name))]
    # if matches:
    #     return matches
    # for guessable in guessables:
    #     if not guessable_view.get_guessable_by_name(guessable):
    #         not_found += ["Guessable {0} not found".format(
    #             guessable)]
    # if not_found:
    #     return not_found
    # this_mode = db_mode.Mode(name=name, guessables=guessables).save()
    # current_user.modes.append(this_mode)
    # current_user.save()
    # return True

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