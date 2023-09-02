from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from my_app import db
from data_manager.dm_sqlite import SqliteDataManager

user_bp = Blueprint('user', __name__)
dm = SqliteDataManager(db.session)


@user_bp.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    """Add movie to user's favorite movies list, and handles any errors.
    If movie is not in database fetches from omdb api"""
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
    """Current logged-in user profile page"""
    user_movies = dm.get_user_movies(user_id=current_user.id)
    user = dm.get_user_by_id(current_user.id)
    return render_template("user/profile.html", user_movies=user_movies, user=user)


@user_bp.route('/update_movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def update_movie(movie_id):
    if request.method == "POST":
        user_id = current_user.id
        dm.update_user_movie(user_id, movie_id, request.form)
        return redirect(url_for("user.profile"))
    movie, user_fields = dm.get_movie_by_id(movie_id, join=True)
    return render_template("user/update_movie.html", movie=movie,
                           user_fields=user_fields)


@user_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    user_id = current_user.id
    dm.delete_user_movie(user_id, movie_id)
    return redirect(url_for("user.profile"))

