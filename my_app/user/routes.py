from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from my_app import db, login_manager
from data_manager.dm_sqlite import SqliteDataManager

user_bp = Blueprint('user', __name__)
dm = SqliteDataManager(db.session)


@user_bp.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    if request.method == "POST":
        user_id = current_user.id
        try:
            dm.add_user_movie(user_id, request.form)
            return redirect(url_for("user.profile"))

        except ValueError as error:
            flash(str(error), "danger")
            return render_template("user/add_movie.html")

    return render_template("user/add_movie.html")


@user_bp.route('/profile')
@login_required
def profile():
    """Profile page"""
    return "Get user movies"


@user_bp.route('/update_movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def user_update_movie(movie_id):
    return "Update user movie"


@user_bp.route('/delete_movie/<int:movie_id>',
               methods=['DELETE'])
@login_required
def user_delete_movie(movie_id):
    return "Delete user movie"
