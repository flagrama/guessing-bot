from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user, logout_user

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
    try:
        current_user.token.delete()
        current_user.token.save()
        current_user.token = None
        current_user.save()
        logout_user()
    except AttributeError:
        session.clear()
    return redirect(url_for('home.homepage'))
