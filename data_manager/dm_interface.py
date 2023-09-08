from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    """Data Manager Interface blueprint class"""
    @abstractmethod
    def save_data(self, new_data):
        """Saves the provided data to file"""

    def get_all_users(self):
        """Returns a list of all users from data file,
        each user data as a dict object."""

    @abstractmethod
    def add_user(self, user_dict):
        """Adds a new user to data file"""

    @abstractmethod
    def delete_user(self, user_id):
        """Deletes a user from data file"""

    @abstractmethod
    def update_user(self, user_id, update_dict):
        """Update user data in data file"""

    @abstractmethod
    def get_user_movies(self, user_id):
        """Returns a list of user movies based on input user_id,
        each movie data as a dict object."""

    @abstractmethod
    def add_user_movie(self, user_id, form_dict):
        """Adds a new movie to specific user in data file"""

    @abstractmethod
    def delete_user_movie(self, user_id, movie_id):
        """Deletes a movie from specific user in data file"""

    @abstractmethod
    def update_user_movie(self, user_id, movie_id, update_dict):
        """Update a movie from specific user in data file"""
