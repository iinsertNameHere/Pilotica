from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, request, Blueprint, flash, redirect, url_for
from werkzeug.security import check_password_hash

from .database import Operator

auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.route("/login", methods = {"POST", "GET"})
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        if Operator.exists(name):
            operator = Operator.query.filter_by(name=name).first()
            if check_password_hash(operator.pwd_hash, password):
                login_user(operator)
                return redirect(url_for('webinterface.interface'))
            else:
                flash("Password is Incorrect!", 'warning')
        else:
            flash("User not found!", 'warning')
    return render_template("login.html.j2")

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))