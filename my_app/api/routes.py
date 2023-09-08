from flask import Blueprint, jsonify, request
from my_app import db
from data_manager.dm_sqlite import SqliteDataManager, User

api_bp = Blueprint("api", __name__, url_prefix="/api")
dm = SqliteDataManager(db.session)
ADD_MOVIE_FIELDS = ["title", "release_year"]
ADD_USER_FIELDS = ["name", "email", "password", "repeat_password"]


def validate_data(json_request, fields):
    """Validates that json request has valid fields"""
    for key, val in json_request.items():
        if key not in fields or val == '':
            return False
    return True


def serialize_movie_object(movie_object):
    """Converts movie object to a dictionary"""
    return {
        "id": movie_object.id,
        "name": movie_object.name,
        "release_year": movie_object.release_year,
        "director": movie_object.director,
        "genre": movie_object.genre,
        "imdb_rating": movie_object.imdb_rating,
        "country": movie_object.country,
        "img_url": movie_object.img,
        "imdb_id": movie_object.imdb_id
    }


def serialize_user_object(user_object):
    """Converts user object to a dictionary"""
    return {
        "id": user_object.id,
        "name": user_object.name,
        "email": user_object.email
    }


@api_bp.route('/users', methods=["GET"])
def get_users():
    """Returns all users from database to user"""
    users = dm.get_all_entries_db(User)
    users_json = []
    for user in users:
        users_json.append(serialize_user_object(user))
    return jsonify(users_json)


@api_bp.route('/user/<int:user_id>', methods=["GET"])
def get_user_movies(user_id):
    """Returns all favorite movies of specified user"""
    user_movies = [movie for _, movie, __ in dm.get_user_movies(user_id)]
    user_movies_json = []
    for movie in user_movies:
        user_movies_json.append(serialize_movie_object(movie))
    return jsonify(user_movies_json)


@api_bp.route('/user/<int:user_id>/add_movie', methods=["POST"])
def add_user_movie(user_id):
    """Adds favorite movie to user, if movie not in db, gets it from api
    The request body should be in json and must have "title" key,
    also the request might have the optional key "release_year".
    Any other keys in request body will cause an error."""
    new_movie_json = request.get_json()
    if not validate_data(new_movie_json, ADD_MOVIE_FIELDS):
        return jsonify({"error": "Bad Request"}), 400

    try:
        new_movie = dm.add_user_movie(user_id, new_movie_json)
        return jsonify(serialize_movie_object(new_movie)), 201

    except ValueError as error:
        return jsonify({"error": str(error)})


@api_bp.route('/add_user', methods=["POST"])
def add_user():
    """Signs new user to database, request body must be in json,
     and have the following keys: "name", "email", "password"
     and "repeat_password".
     Any other keys in request body will cause an error."""
    new_user_json = request.get_json()
    if not validate_data(new_user_json, ADD_USER_FIELDS):
        return jsonify({"error": "Bad Request"}), 400

    try:
        new_user = dm.add_user(new_user_json, api=True)
        return jsonify(serialize_user_object(new_user)), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

