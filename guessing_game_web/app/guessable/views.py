import string
from flask import request, flash, render_template, redirect, url_for
from flask_login import login_required, current_user
import flask_mongoengine as mongoengine
from guessing_game_web.app.models import exception, form, user, guessable as db_guessable
from guessing_game_web.app.mode import views as mode_view
from . import guessable

def __get_guessable_id_by_name(guessable_name):
    named_guessable = None
    for this_guessable in current_user.guessables:
        if string.capwords(this_guessable.name) == string.capwords(guessable_name):
            named_guessable = this_guessable.id
            break
    return named_guessable

def __get_guessable(guessable_id):
    if not getattr(user.User, 'objects')(
            username=current_user.username, guessables__contains=guessable_id):
        raise exception.UserAccessException
    this_guessable = getattr(db_guessable.Guessable, 'objects').get(id=guessable_id)
    if this_guessable:
        return this_guessable
    return this_guessable

def __add_guessable(this_form):
    name = string.capwords(this_form.name.data)
    codes = this_form.codes.data.lower().split(',')
    codes = list(set(codes))
    matches = []
    for this_guessable in current_user.guessables:
        if this_guessable.name.lower() == name.lower():
            return "Guessable name {0} already exists".format(name)
        code_matches = set(this_guessable.codes).intersection(set(codes))
        if code_matches:
            matches += ["Guessable code(s) {0} already exists in {1}".format(
                ', '.join(code_matches), this_guessable.name)]
    if matches:
        return matches
    this_guessable = db_guessable.Guessable(name=name, codes=codes).save()
    current_user.guessables.append(this_guessable)
    current_user.save()
    return True

def __update_guessable(this_form):
    key = this_form.key.data
    name = string.capwords(this_form.name.data)
    codes = this_form.codes.data.lower().split(',')
    codes = list(set(codes))
    matches = []
    for this_guessable in current_user.guessables:
        if str(this_guessable.id) == key:
            continue
        if this_guessable.name.lower() == name.lower():
            return "Guessable name {0} already exists".format(name)
        code_matches = set(this_guessable.codes).intersection(set(codes))
        if code_matches:
            matches += ["Guessable code(s) {0} already exists in {1}".format(
                ', '.join(code_matches), this_guessable.name)]
    if matches:
        return matches
    __get_guessable(this_form.key.data).update(name=name, codes=codes)
    current_user.save()
    return True

def __delete_guessable(guessable_id):
    this_guessable = __get_guessable(guessable_id)
    user_mode_ids = mode_view.get_modes_by_item_name(this_guessable.name)
    if user_mode_ids:
        for mode_id in user_mode_ids:
            getattr(db_guessable.Mode, 'objects')(
                id=mode_id).update_one(
                    pull__guessables=this_guessable.name)
            this_mode = mode_view.get_mode(mode_id)
            if this_mode:
                if not this_mode.guessables:
                    getattr(user.User, 'objects')(
                        id=current_user.id, modes=this_mode).update_one(
                            pull__modes=this_mode)
                    this_mode.delete()
    existing_name = this_guessable.name
    getattr(user.User, 'objects')(
        id=current_user.id).update_one(
            pull__guessables=this_guessable)
    this_guessable.delete()
    current_user.save()
    return existing_name

def get_guessable_by_name(guessable_name):
    guessable_id = __get_guessable_id_by_name(guessable_name)
    if not guessable_id:
        return None
    return __get_guessable(guessable_id)

@guessable.route('add', methods=['GET', 'POST'])
@login_required
def add():
    this_form = form.AddGuessable()
    if request.method == 'POST':
        success = True
        if this_form.validate():
            result = __add_guessable(this_form)
            if isinstance(result, list) and not isinstance(result, str):
                for message in result:
                    flash(message, 'danger')
                    success = False
            elif isinstance(result, str):
                flash(result, 'danger')
                success = False
            if success:
                flash("Created {0}".format(string.capwords(this_form.name.data)), 'success')
                return redirect(url_for('home.dashboard'))
        else:
            flash('All fields are required', 'danger')
    return render_template('guessable/add.html', title="Add Guessable", tab="dashboard", form=this_form)

@guessable.route('update/<guessable_id>', methods=['GET', 'POST'])
@login_required
def update(guessable_id):
    this_form = form.UpdateGuessable()
    if request.method == 'POST':
        success = True
        if this_form.validate():
            result = __update_guessable(this_form)
            if isinstance(result, list) and not isinstance(result, str):
                for message in result:
                    flash(message, 'danger')
                    success = False
            elif isinstance(result, str):
                flash(result, 'danger')
                success = False
            if success:
                flash("Updated {0}".format(string.capwords(this_form.name.data)), 'success')
                return redirect(url_for('home.dashboard'))
        else:
            flash('All fields are required', 'danger')
    try:
        this_guessable = __get_guessable(guessable_id)
    except (mongoengine.DoesNotExist,
            mongoengine.ValidationError,
            exception.UserAccessException):
        return redirect(url_for('home.dashboard'))
    return render_template(
        'guessable/update.html',
        title="Update {0}".format(this_guessable.name),
        tab="dashboard",
        existing_key=this_guessable.id,
        existing_name=this_guessable.name,
        existing_codes=','.join(this_guessable.codes),
        form=this_form)

@guessable.route('delete/<guessable_id>', methods=['GET'])
@login_required
def delete(guessable_id):
    try:
        result = __delete_guessable(guessable_id)
    except (mongoengine.DoesNotExist,
            mongoengine.ValidationError,
            exception.UserAccessException):
        return redirect(url_for('home.dashboard'))
    flash("Deleted {0}".format(result), 'success')
    return redirect(url_for('home.dashboard'))
