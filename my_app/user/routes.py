from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from my_app import db
from data_manager.dm_sqlite import SqliteDataManager, Movie

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
    user = dm.get_entry_by_id(current_user.id)
    return render_template("user/profile.html", user_movies=user_movies, user=user)


@user_bp.route('/add_review/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def add_review(movie_id):
    """GET: Renders add review page
    POST: Adds user review to the specified movie"""
    if request.method == "POST":
        user_id = current_user.id
        dm.add_movie_review(user_id, movie_id, request.form)
        return redirect(url_for("user.review_page", movie_id=movie_id))
    movie = dm.get_entry_by_id(movie_id, db_model=Movie)
    return render_template("user/add_review.html", movie=movie)


@user_bp.route('/movie/<int:movie_id>/review/')
@login_required
def review_page(movie_id):
    """Renders movie review page of the current user by the movie id"""
    _, user, movie, review = dm.get_user_movie_by_ids(current_user.id,
                                                      movie_id, join=True)
    return render_template("/user/review.html", user=user, movie=movie,
                           review=review)


@user_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    """Deletes movie from user's favorite movies,
    by deleting it from users_movies database"""
    user_id = current_user.id
    dm.delete_user_movie(user_id, movie_id)
    return redirect(url_for("user.profile"))


@user_bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    """Deletes the user from database"""
    user_id = current_user.id
    dm.delete_user(user_id)
    return redirect(url_for("main.home"))


@user_bp.route('/update_user', methods=['GET', 'POST'])
@login_required
def update_user():
    """GET: Renders update user page
    POST: Updates user details"""
    if request.method == "POST":
        dm.update_user(current_user.id, request.form)
    user = dm.get_entry_by_id(current_user.id, )
    return render_template("user/update_user.html", user=user)


@user_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Authenticates and validates request, if tests pass, updates user
    password in database and redirects back to profile page"""
    input_password = request.form.get("current_password")
    password = request.form.get("password")
    repeat_password = request.form.get("repeat_password")
    if dm.authenticate_password(current_user, input_password) and \
            dm.passwords_match(password, repeat_password):
        dm.update_user(current_user.id, request.form)
    return redirect(url_for("user.profile"))
