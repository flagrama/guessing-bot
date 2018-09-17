from flask import request, flash, render_template, redirect, url_for
from flask_login import login_required, current_user
from guessing_game_web.app import db
from guessing_game_web.app.models import form, user, guessable as db_guessable
from . import guessable

def get_user_guessable(guessable_id):
    try:
        user_guessable = user.User.objects( # pylint: disable=no-member
            username=current_user.username, guessables__contains=guessable_id)
    except (user.User.DoesNotExist, db.ValidationError) as exception: # pylint: disable=no-member
        flash("Access Violation! {0}".format(exception), 'danger')
        return None
    return user_guessable

def get_guessable(guessable_id):
    if not get_user_guessable(guessable_id):
        return None
    return db_guessable.Guessable.objects.get(id=guessable_id) # pylint: disable=no-member

def add_guessable(this_form):
    name = this_form.name.data
    codes = this_form.codes.data.split(',')
    this_guessable = db_guessable.Guessable(name=name, codes=codes).save()
    current_user.guessables.append(this_guessable)
    current_user.save()

def update_guessable(this_form):
    name = this_form.name.data
    codes = this_form.codes.data.split(',')
    this_guessable = get_guessable(this_form.key.data)
    if not this_guessable:
        return False
    this_guessable.update(set__name=name, set__codes=codes)
    this_guessable.save()
    current_user.save()
    return True

def delete_guessable(guessable_id):
    this_guessable = get_guessable(guessable_id)
    user_guessable = get_user_guessable(guessable_id)
    if not this_guessable or not user_guessable:
        return False
    existing_name = this_guessable.name
    user_guessable.update_one(pull__guessables=this_guessable)
    this_guessable.delete()
    current_user.save()
    return existing_name

@guessable.route('add', methods=['GET', 'POST'])
@login_required
def add():
    this_form = form.AddGuessable()

    if request.method == 'POST':
        if this_form.validate():
            add_guessable(this_form)
            flash("Successfully created Guessable", 'success')
            return redirect(url_for('home.dashboard'))
        flash('All fields are required', 'danger')

    return render_template('guessable/add.html', title="Add Guessable", form=this_form)

@guessable.route('update/<guessable_id>', methods=['GET', 'POST'])
@login_required
def update(guessable_id):
    this_form = form.UpdateGuessable()

    if request.method == 'POST':
        if this_form.validate():
            result = update_guessable(this_form)
            if not result:
                return redirect(url_for('home.logout'))
            flash("Successfully updated {0}".format(this_form.name.data), 'success')
            return redirect(url_for('home.dashboard'))
        flash('All fields are required', 'danger')

    this_guessable = get_guessable(guessable_id)
    return render_template(
        'guessable/update.html',
        title="Update {0}".format(this_guessable.name),
        existing_key=this_guessable.id,
        existing_name=this_guessable.name,
        existing_codes=','.join(this_guessable.codes),
        form=this_form)

@guessable.route('delete/<guessable_id>', methods=['GET'])
@login_required
def delete(guessable_id):
    result = delete_guessable(guessable_id)
    if not result:
        return redirect(url_for('home.logout'))
    flash("Successfully deleted {0}".format(result), 'success')
    return redirect(url_for('home.dashboard'))
