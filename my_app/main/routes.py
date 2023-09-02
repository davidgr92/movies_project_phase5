from flask import Blueprint, render_template
from flask_login import login_required
from my_app import db, login_manager
from data_manager.dm_sqlite import SqliteDataManager, User, Movie

main_bp = Blueprint("main", __name__)
dm = SqliteDataManager(db.session)


@main_bp.route('/')
@login_required
def home():
    users = dm.get_all_entries_db(User)
    movies = dm.get_all_entries_db(Movie)
    return render_template("main/index.html", users=users, movies=movies)


@main_bp.route('/all_movies')
def all_movies():
    movies = dm.get_all_entries_db(Movie)
    return render_template("main/all_movies.html", movies=movies)
    # TODO Add a favorite icon button to the movies and add the functionality
    #  that it will be added to user's favorite movies


@main_bp.route('/user/<int:user_id>')
def user_public_profile(user_id):
    user_movies = dm.get_user_movies(user_id=user_id)
    public_user_page = dm.get_user_by_id(user_id)
    return render_template("user/profile.html", user_movies=user_movies, user=public_user_page)
    # return f"User {user_id} public profile"


@main_bp.app_errorhandler(404)
def error_404(error):
    """Handle error 404"""
    return render_template('main/404.html'), 404


@main_bp.app_errorhandler(500)
def error_500(error):
    """Handle error 500"""
    return render_template('main/500.html'), 500


# TODO - Update home html to show all/most movies from database,
#  display them in grid showing the poster img, genre,
#  and linking to public movie page.
#  also show list of users (Add user profile img to users db)
#  and display grid of registered users (Name and profile img)
#  and link to the user public page.
#  current_user.id - gets

