from datetime import datetime
from flask import flash
from sqlalchemy import func
from data_manager.dm_interface import DataManagerInterface
from my_app.models.data_models import Movie, User, UserMovies
from my_app import bcrypt
from apis.omdb_api import MovieAPIConnection


class SqliteDataManager(DataManagerInterface):
    def __init__(self, db_session):
        self.db_session = db_session
        self.query = db_session.query

    @staticmethod
    def passwords_match(password, repeat_password):
        """Check that passwords match"""
        if password == repeat_password:
            return True
        flash("Passwords don't match.", "danger")
        return False

    @staticmethod
    def get_user_by_email(email):
        """Returns a user entry based on user email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_id(user_id):
        """Returns a user entry based on user id"""
        return User.query.filter_by(id=int(user_id)).first()

    @staticmethod
    def get_movie_by_name(movie_name):
        """Checks if movie exists in database, if it does then returns it"""
        return Movie.query.filter(Movie.name.ilike(movie_name)).first()

    # @staticmethod
    def get_movie_by_id(self, movie_id, join=False):
        """Returns a user entry based on user id"""
        if join:
            return self.query(Movie, UserMovies).join(UserMovies).filter_by(
                movie_id=int(movie_id)).first()
        return Movie.query.filter_by(id=int(movie_id)).first()

    @staticmethod
    def get_user_movie_by_ids(user_id, movie_id):
        """Returns a user entry based on user id"""
        return UserMovies.query.filter_by(user_id=int(user_id),
                                          movie_id=int(movie_id)).first()

    def is_email_unique(self, email):
        """Check that email is not in users database"""
        user = self.get_user_by_email(email)
        if user is None:
            return True
        flash("Email already exists", "danger")
        return False

    def save_data(self, new_data=None):
        """Saves the provided data to database"""
        if new_data:
            self.db_session.add(new_data)
        self.db_session.commit()

    def get_all_entries_db(self, db_model):
        """Returns a list of all users from database"""
        return self.query(db_model).all()

    def add_user(self, user_dict):
        """Adds a new user to data file"""
        name = user_dict.get("name")
        email = user_dict.get("email")
        password = user_dict.get("password")
        repeat_password = user_dict.get("repeat_password")

        if self.passwords_match(password, repeat_password)\
                and self.is_email_unique(email):
            new_user = User(email=email, password=password, name=name)
            flash(f"Successfully registered {new_user}", "success")
            self.save_data(new_user)
            return new_user

    def authenticate_login(self, login_dict):
        """Authenticates user login attempt, if valid return user,
        otherwise returns none"""
        email = login_dict.get("email")
        password = login_dict.get("password")
        user = self.get_user_by_email(email)
        if user and bcrypt.check_password_hash(user.password, password):
            return user

    def delete_user(self, user_id):
        """Deletes a user from data file"""
        pass

    def update_user(self, user_id, update_dict):
        """Update user data in data file"""
        pass

    def get_user_movies(self, user_id, title=None):
        """Returns a list of user favorite movies based on user_id,
        if title is provided returns only movie with this title
        """
        if title:
            return self.query(UserMovies, Movie).join(Movie).\
                filter(UserMovies.user_id == user_id,
                       Movie.name.ilike(title)).first()
        return self.query(UserMovies, Movie).join(Movie).\
            filter(UserMovies.user_id == user_id).all()

    def add_user_movie(self, user_id, form_dict):
        """Adds a new movie to specific user in data file"""
        movie_name = form_dict.get("title")
        year = form_dict.get("release_year")

        movie = self.get_user_movies(user_id, title=movie_name)
        if movie:
            raise ValueError("Movie already favorite by user")

        new_movie = self.get_movie_by_name(movie_name)
        if new_movie is None:
            self.add_movie_from_api(movie_name, year)
            new_movie = self.get_movie_by_name(movie_name)

        user_movie = UserMovies(user_id=user_id,
                                movie_id=new_movie.id)
        self.save_data(user_movie)
        flash(f"New movie {new_movie.name} successfully added to user",
              "success")

    def add_movie_from_api(self, movie_name, year):
        connection = MovieAPIConnection()
        new_movie = connection.get_movie_data(movie_name, year)

        if 'error' in new_movie:
            raise ValueError(new_movie['error'])

        movie_obj = Movie(name=new_movie['name'],
                          release_year=new_movie['year'],
                          director=new_movie['director'],
                          imdb_id=new_movie['imdbID'],
                          imdb_rating=new_movie['rating'],
                          genre=new_movie['genre'],
                          img=new_movie['img'],
                          country=new_movie['country'],
                          country_alpha_2=new_movie['alpha_2'])
        self.save_data(movie_obj)
        flash(f"Successfully registered {movie_obj.name} to database", "success")

    def update_user_movie(self, user_id, movie_id, update_dict):
        """Update a movie from specific user in UserMovies database"""
        user_movie = self.get_user_movie_by_ids(user_id, movie_id)
        user_rating = update_dict.get("user_rating")
        user_note = update_dict.get("note")
        if user_rating:
            user_movie.user_rating = user_rating

        if user_note != "":
            user_movie.user_note = user_note

        if user_rating or user_note != "":
            self.save_data()
            flash("Successfully updated entry", "success")

    def delete_user_movie(self, user_id, movie_id):
        """Deletes a movie from specific user in data file"""
        user_movie = self.get_user_movie_by_ids(user_id, movie_id)
        self.db_session.delete(user_movie)
        self.save_data()
        flash("User favorite movie successfully deleted", "success")
