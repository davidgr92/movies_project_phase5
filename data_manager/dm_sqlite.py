from flask import flash
from data_manager.dm_interface import DataManagerInterface
from my_app.models.data_models import Movie, User, UserMovies, Review
from my_app import bcrypt
from apis.omdb_api import MovieAPIConnection


class SqliteDataManager(DataManagerInterface):
    """Data manager class which interfaces with the sqlite database"""

    def __init__(self, db_session):
        self.db_session = db_session
        self.query = db_session.query

    def save_data(self, new_data=None):
        """Saves the provided data to database"""
        if new_data:
            self.db_session.add(new_data)
        self.db_session.commit()

    @staticmethod
    def passwords_match(password, repeat_password):
        """Check that passwords match"""
        if password == repeat_password:
            return True
        raise ValueError("Passwords don't match.")

    @staticmethod
    def authenticate_password(user, input_password):
        """Check that password matches encrypted password
        in user entry in database"""
        if bcrypt.check_password_hash(user.password, input_password):
            return True
        return False

    def authenticate_login(self, login_dict):
        """Authenticates user login attempt, if valid return user,
        otherwise returns none"""
        email = login_dict.get("email")
        password = login_dict.get("password")
        user = self.get_user_by_email(email)
        if user and self.authenticate_password(user, password):
            return user

    def is_email_unique(self, email):
        """Check that email is not in users database"""
        user = self.get_user_by_email(email)
        if user is None:
            return True
        raise ValueError("Email already exists")

    @staticmethod
    def get_user_by_email(email):
        """Returns a user entry based on user email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_entry_by_id(model_id, db_model=User):
        """Returns an entry based on id from provided db_model"""
        return db_model.query.filter_by(id=int(model_id)).first()

    @staticmethod
    def get_movie_by_name(movie_name):
        """Checks if movie exists in database, if it does then returns it"""
        return Movie.query.filter(Movie.name.ilike(movie_name)).first()

    def get_user_movie_by_ids(self, user_id, movie_id, join=None):
        """Returns a user movie entry based on user id and movie id"""
        if join:
            return self.query(UserMovies, User, Movie, Review)\
                .filter_by(user_id=int(user_id), movie_id=int(movie_id)) \
                .join(User).join(Movie).join(Review)\
                .first()
        return UserMovies.query.filter_by(user_id=int(user_id),
                                          movie_id=int(movie_id)).first()

    def get_all_entries_db(self, db_model):
        """Returns a list of all users from database"""
        return self.query(db_model).all()

    def add_user(self, user_dict, api=False):
        """Adds a new user to data file"""
        name = user_dict.get("name")
        email = user_dict.get("email")
        password = user_dict.get("password")
        repeat_password = user_dict.get("repeat_password")

        try:
            if self.passwords_match(password, repeat_password)\
                    and self.is_email_unique(email):
                new_user = User(email=email, password=password, name=name)
                flash(f"Successfully registered {new_user}", "success")
                self.save_data(new_user)
                return new_user
        except ValueError as error:
            if api:
                raise ValueError(error) from error
            flash(str(error), "danger")

    def delete_user(self, user_id):
        """Deletes a user from data file"""
        self.db_session.query(UserMovies).\
            filter(UserMovies.user_id == user_id).delete()
        self.save_data()

        user = self.get_entry_by_id(user_id)
        self.db_session.delete(user)
        self.save_data()
        flash("User successfully deleted", "success")

    def update_user(self, user_id, update_dict):
        """Update user data in data file"""
        user = self.get_entry_by_id(user_id)
        password = update_dict.get("password")
        print(f"pass {password}")
        email = update_dict.get("user_email")
        print(f"Email {email}")
        name = update_dict.get("user_name")
        print(f"Name {name}")

        if password:
            hashed_pass = bcrypt.generate_password_hash(password)
            user.password = hashed_pass

        if name:
            user.name = name

        if email:
            user.email = email

        if password or name or email:
            self.save_data()
            flash("Successfully updated user details", "success")

    def get_user_movies(self, user_id, title=None):
        """Returns a list of user favorite movies based on user_id,
        if title is provided returns only movie with this title
        """
        if title:
            return self.query(UserMovies, Movie, Review).join(Movie).outerjoin(Review)\
                .filter(UserMovies.user_id == user_id,
                        Movie.name.ilike(title)).first()
        return self.query(UserMovies, Movie, Review).join(Movie).outerjoin(Review)\
            .filter(UserMovies.user_id == user_id).all()

    def add_user_movie(self, user_id, form_dict):
        """Adds a new movie to specific user in data file"""
        movie_name = form_dict.get("title")
        year = form_dict.get("release_year")

        movie = self.get_user_movies(user_id, title=movie_name)
        if movie:
            raise ValueError("Movie already favorite by user")

        new_movie = self.get_movie_by_name(movie_name)
        if new_movie is None:
            movie_from_api = self.add_movie_from_api(movie_name, year)
            new_movie = self.get_movie_by_name(movie_from_api.name)

        user_movie = UserMovies(user_id=user_id,
                                movie_id=new_movie.id)
        self.save_data(user_movie)
        flash(f"New movie {new_movie.name} successfully added to user",
              "success")
        return new_movie

    def add_movie_from_api(self, movie_name, year):
        """Get movie from api and add to movies database"""
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

        # Check if fetched movie name already in database
        movie_from_api = self.get_movie_by_name(movie_obj.name)
        if movie_from_api:
            return movie_from_api

        self.save_data(movie_obj)
        flash(f"Successfully registered {movie_obj.name} to database", "success")
        return movie_obj

    def update_user_movie(self, user_id, movie_id, update_dict):
        """Update a movie from specific user in UserMovies database"""

    def add_movie_review(self, user_id, movie_id, update_dict):
        """Update a movie from specific user in UserMovies database"""
        review_rating = update_dict.get("review_rating")
        review_text = update_dict.get("review_text")
        short_note = update_dict.get("short_note")

        user_movie = self.get_user_movie_by_ids(user_id, movie_id)
        if user_movie.review_id:
            movie_review = self.get_entry_by_id(user_movie.review_id,
                                                db_model=Review)
            movie_review.rating = review_rating
            movie_review.text = review_text
            if short_note != "":
                movie_review.short_note = short_note
            operation = "updated"
            self.save_data()
        else:
            movie_review = Review(rating=review_rating, text=review_text)
            operation = "added"
            if short_note != "":
                movie_review.short_note = short_note
            self.save_data(movie_review)

        user_movie.review_id = movie_review.id
        self.save_data()
        flash(f"Successfully {operation} {movie_review}", "success")

    def delete_user_movie(self, user_id, movie_id):
        """Deletes a movie from specific user in data file"""
        user_movie = self.get_user_movie_by_ids(user_id, movie_id)
        if user_movie.review_id:
            review = self.get_entry_by_id(user_movie.review_id, Review)
            self.db_session.delete(review)
            self.save_data()
        self.db_session.delete(user_movie)
        self.save_data()
        flash("User favorite movie successfully deleted", "success")
