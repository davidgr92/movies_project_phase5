from flask import Blueprint, render_template
from flask_login import login_required
from my_app import db
from data_manager.dm_sqlite import SqliteDataManager, User, Movie

main_bp = Blueprint("main", __name__)
dm = SqliteDataManager(db.session)


@main_bp.route('/')
@login_required
def home():
    """Renders home page"""
    users = dm.get_all_entries_db(User)
    movies = dm.get_all_entries_db(Movie)
    return render_template("main/index.html", users=users, movies=movies[:10])


@main_bp.route('/all_movies')
def all_movies():
    """Renders all movies page"""
    movies = dm.get_all_entries_db(Movie)
    return render_template("main/all_movies.html", movies=movies)


@main_bp.route('/user/<int:user_id>')
def user_public_profile(user_id):
    """Renders user public page"""
    user_movies = dm.get_user_movies(user_id=user_id)
    public_user_page = dm.get_entry_by_id(user_id)
    return render_template("user/profile.html", user_movies=user_movies, user=public_user_page)


@main_bp.route('/movie/<int:movie_id>')
def movie_page(movie_id):
    """Renders movie public page"""
    movie = dm.get_entry_by_id(movie_id, db_model=Movie)
    return render_template("main/movie.html", movie=movie)


@main_bp.app_errorhandler(404)
def error_404(error):
    """Handle error 404"""
    return render_template('main/404.html'), 404


@main_bp.app_errorhandler(500)
def error_500(error):
    """Handle error 500"""
    return render_template('main/500.html'), 500
