import string
from flask import request, flash, render_template, redirect, url_for
from flask_login import login_required, current_user
from guessing_game_web.app import db
from guessing_game_web.app.models import form, user, guessable as db_mode
from guessing_game_web.app.guessable import views as guessable_view
from . import mode

def __get_user_mode_ids_by_item(item_name):
    user_modes = []
    for this_mode in current_user.modes:
        for item in this_mode.guessables:
            if string.capwords(item) == string.capwords(item_name):
                user_modes += [str(this_mode.id)]
    return user_modes

def get_modes_by_item_name(mode_item_name):
    mode_ids = __get_user_mode_ids_by_item(mode_item_name)
    if not mode_ids:
        return None
    these_modes = []
    for mode_id in mode_ids:
        try:
            this_mode = db_mode.Mode.objects.get(id=mode_id) # pylint: disable=no-member
            these_modes += [str(this_mode.id)]
        except (user.User.DoesNotExist, db.ValidationError): # pylint: disable=no-member
            return None
    return these_modes

def get_user_mode(mode_id):
    try:
        user_mode = user.User.objects( # pylint: disable=no-member
            username=current_user.username, modes__contains=mode_id)
    except (user.User.DoesNotExist, db.ValidationError): # pylint: disable=no-member
        flash("Access Violation!", 'danger')
        return None
    return user_mode

def get_mode(mode_id):
    get_user_mode(mode_id)
    try:
        this_mode = db_mode.Mode.objects.get(id=mode_id) # pylint: disable=no-member
    except (user.User.DoesNotExist, db.ValidationError): # pylint: disable=no-member
        flash("Access Violation!", 'danger')
        return None
    return this_mode

def __add_mode(this_form):
    name = this_form.name.data.lower()
    guessables = this_form.guessables.data.split(',')
    guessables = list(set(string.capwords(i) for i in guessables))
    matches = []
    for this_mode in current_user.modes:
        if string.capwords(this_mode.name) == string.capwords(name):
            return "Mode name {0} already exists".format(string.capwords(name))
        item_matches = set(this_mode.guessables).intersection(set(guessables))
        if item_matches:
            matches += ["Mode item(s) {0} already exists in {1}".format(
                ', '.join(item_matches), string.capwords(this_mode.name))]
    if matches:
        return matches
    for guessable in guessables:
        if not guessable_view.get_guessable_by_name(guessable):
            return "Guessable {0} not found in {1}'s guessables".format(
                guessable, current_user.username)
    this_mode = db_mode.Mode(name=name, guessables=guessables).save()
    current_user.modes.append(this_mode)
    current_user.save()
    return True

def __update_mode(this_form):
    key = this_form.key.data
    name = this_form.name.data.lower()
    guessables = this_form.guessables.data.split(',')
    guessables = list(set(string.capwords(i) for i in guessables))
    matches = []
    for this_mode in current_user.modes:
        if str(this_mode.id) == key:
            continue
        if string.capwords(this_mode.name) == string.capwords(name):
            return "Mode name {0} already exists".format(string.capwords(name))
        item_matches = set(this_mode.guessables).intersection(set(guessables))
        if item_matches:
            matches += ["Mode item(s) {0} already exists in {1}".format(
                ', '.join(item_matches), string.capwords(this_mode.name))]
    if matches:
        return matches
    this_mode = get_mode(this_form.key.data)
    if not this_mode:
        return False
    this_mode.update(set__name=name, set__guessables=guessables)
    this_mode.save()
    current_user.save()
    return True

def __delete_mode(mode_id):
    this_mode = get_mode(mode_id)
    user_mode = get_user_mode(mode_id)
    if not this_mode or not user_mode:
        return False
    existing_name = this_mode.name
    user_mode.update_one(pull__modes=this_mode)
    this_mode.delete()
    current_user.save()
    return existing_name

@mode.route('add', methods=['GET', 'POST'])
@login_required
def add():
    this_form = form.AddMode()

    if request.method == 'POST':
        success = True
        if this_form.validate():
            result = __add_mode(this_form)
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

    return render_template('mode/add.html', title="Add Mode", form=this_form)

@mode.route('update/<mode_id>', methods=['GET', 'POST'])
@login_required
def update(mode_id):
    this_form = form.UpdateMode()

    if request.method == 'POST':
        success = True
        if this_form.validate():
            result = __update_mode(this_form)
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

    this_mode = get_mode(mode_id)
    if not this_mode:
        return redirect(url_for('home.logout'))
    return render_template(
        'mode/update.html',
        title="Update {0}".format(this_mode.name),
        existing_key=this_mode.id,
        existing_name=this_mode.name,
        existing_guessables=','.join(this_mode.guessables),
        form=this_form)

@mode.route('delete/<mode_id>', methods=['GET'])
@login_required
def delete(mode_id):
    result = __delete_mode(mode_id)
    if not result:
        return redirect(url_for('home.logout'))
    flash("Deleted {0}".format(result), 'success')
    return redirect(url_for('home.dashboard'))
