from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user # pylint: disable=import-error

from . import home

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")

@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template('home/dashboard.html', title="Dashboard")

@home.route("/logout/")
def logout():
    if current_user.is_authenticated:
        current_user.token.delete()
        current_user.token.save()
        current_user.token = None
        current_user.save()
        logout_user()
    flash('You have successfully been logged out.')
    return redirect(url_for('home.homepage'))
