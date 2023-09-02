from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import logout_user, login_user, login_required, current_user
from my_app import db, login_manager
from data_manager.dm_sqlite import SqliteDataManager

auth_bp = Blueprint('auth', __name__)
dm = SqliteDataManager(db.session)


@login_manager.user_loader
def load_user(user_id):
    """Fetches user by id from database and loads it to session"""
    return dm.get_user_by_id(user_id)


@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    """Register new user to database
    GET: Render html template of register page
    POST: Validate form data if valid adds user to database and login,
    otherwise flashes the error and reloads the page.
    """
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("main.home"))
    if request.method == "POST":
        new_user = dm.add_user(request.form)
        if new_user:
            login_user(new_user)
            return redirect(url_for("main.home"))
    return render_template("auth/register.html")


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    """Login in to the application
    GET: Render html template of login page
    POST: Authenticate login form data, if valid login user,
    otherwise flashes the error and reloads the page.
    """
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("main.home"))
    if request.method == "POST":
        user = dm.authenticate_login(request.form)
        if user:
            login_user(user)
            return redirect(url_for("user.profile"))
        else:
            flash("Invalid email and/or password.", "danger")
    return render_template("auth/login.html")


@auth_bp.route('/logout')
@login_required
def logout():
    """Log user out of the session"""
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("auth.login"))
