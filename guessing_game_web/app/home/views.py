from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user # pylint: disable=import-error
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

from . import home

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")

@home.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    form = Form(request.form)

    #print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        surname=request.form['surname']
        email=request.form['email']
        password=request.form['password']

        if form.validate():
            flash('Hello: {} {}'.format(name, surname))

        else:
            flash('Error: All Fields are Required')

    return render_template('home/dashboard.html', title="Dashboard", form=form)

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
