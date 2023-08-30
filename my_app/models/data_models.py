from flask_login import UserMixin
from my_app import bcrypt, db


class Movie(db.Model):
    """
    Movie model class, which sets the columns for "movies" table
    """
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    release_year = db.Column(db.String(4), nullable=False)
    director = db.Column(db.String, nullable=False)

    imdb_id = db.Column(db.String)
    imdb_rating = db.Column(db.Float)
    genre = db.Column(db.String)
    img = db.Column(db.String)
    country = db.Column(db.String)
    country_alpha_2 = db.Column(db.String(2))

    def __repr__(self):
        return f"<Movie(id = {self.id}, name = {self.name}, " \
               f"release_year = {self.release_year})>"

    def __str__(self):
        return f"Name: {self.name}, id: {self.id}"


class User(UserMixin, db.Model):
    """
    User model class, which sets the columns for "users" table
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    profile_img = db.Column(db.String, nullable=True)

    def __init__(self, email, password, name):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.name = name
        self.profile_img = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"

    def __repr__(self):
        return f"<User(id = {self.id}, email = {self.email})>"

    def __str__(self):
        return f"email: {self.email}"


class UserMovies(db.Model):
    """
    UserMovie model class, which sets the columns for "users_movies" table.
    Represents the favorite movies for each user.
    """
    __tablename__ = "users_movies"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"),
                         nullable=False)
    user_rating = db.Column(db.Float)
    user_note = db.Column(db.Float)

    __table_args__ = (db.PrimaryKeyConstraint(user_id, movie_id,),)

    def __repr__(self):
        return f"<UserMovie(user_id = {self.user_id}, " \
               f"movie = {self.movie_id})>"

    def __str__(self):
        return f"User: {self.user_id}, Movie: {self.movie_id}"
