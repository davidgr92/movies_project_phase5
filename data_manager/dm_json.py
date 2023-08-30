import json
from os.path import isfile
from data_manager.dm_interface import DataManagerInterface


class JSONDataManager(DataManagerInterface):
    """Data manager class which interfaces with the JSON data file"""
    def __init__(self, filename="data_manager/data/data.json"):
        self.filename = filename
        if not isfile(filename):
            self.save_data([])

    def save_data(self, data) -> None:
        """Saves the provided data to the json data file"""
        with open(self.filename, 'w') as file:
            file.write(json.dumps(data, indent=4))

    def get_all_users(self) -> list:
        """Returns a list of all users from data file,
        each user data as a dict object."""
        with open(self.filename, 'r') as file:
            return json.loads(file.read())

    def is_user_key_exists(self, val, key='id'):
        """Checks if specific user key-val pair exists in data file,
        Returns boolean value accordingly"""
        for user in self.get_all_users():
            if user[key] == val:
                return True
        return False

    def add_user(self, user_dict) -> None:
        """Adds a new user to data file"""
        users_list = self.get_all_users()
        user_ids = (user['id'] for user in users_list)
        if user_dict['id'] not in user_ids:
            users_list.append(user_dict)
            self.save_data(users_list)

    def delete_user(self, user_id) -> None:
        """Deletes a user from data file"""
        users_list = self.get_all_users()
        for user in users_list:
            if user['id'] == user_id:
                users_list.remove(user)
        self.save_data(users_list)

    def update_user(self, user_id, update_dict) -> None:
        """Update user data in data file"""
        users_list = self.get_all_users()
        for user in users_list:
            if user['id'] == user_id:
                user.update(update_dict)
        self.save_data(users_list)

    def get_user_by_key(self, search_val, key='id') -> dict:
        """Returns a user dict based on specified key,
        by default key is 'id'"""
        users_list = self.get_all_users()
        for user in users_list:
            if user[key] == search_val:
                return user

    def get_user_movies(self, user_id) -> list:
        """Returns a list of user movies based on input user_id,
        each movie data as a dict object."""
        return self.get_user_by_key(user_id)['movies']

    def get_user_single_movie(self, user_id, movie_id) -> dict:
        """Returns a dictionary with the specific user movie"""
        user_movies = self.get_user_movies(user_id)
        for movie in user_movies:
            if movie['id'] == movie_id:
                return movie

    def add_user_movie(self, user_id, movie_dict) -> None:
        """Adds a new movie to specific user in data file"""
        users_list = self.get_all_users()
        for user in users_list:
            if user['id'] == user_id:
                movie_names = (movie['name'] for movie in user['movies'])
                if movie_dict['name'] not in movie_names:
                    user['movies'].append(movie_dict)
                else:
                    raise ValueError("Movie already exists, try again")
        self.save_data(users_list)

    def is_movie_id_exists(self, user_id, movie_id) -> bool:
        """Checks if movie_id exists in users movies list,
        Returns boolean value accordingly"""
        for movie in self.get_user_movies(user_id):
            if movie['id'] == movie_id:
                return True
        return False

    def delete_user_movie(self, user_id, movie_id) -> None:
        """Deletes a movie from specific user in data file"""
        users_list = self.get_all_users()
        for user in users_list:
            if user['id'] == user_id:
                for movie in user['movies']:
                    if movie['id'] == movie_id:
                        user['movies'].remove(movie)
        self.save_data(users_list)

    def update_user_movie(self, user_id, movie_id, update_dict) -> None:
        """Update a movie from specific user in data file"""
        users_list = self.get_all_users()
        for user in users_list:
            if user['id'] == user_id:
                for movie in user['movies']:
                    if movie['id'] == movie_id:
                        movie.update(update_dict)
                        if not update_dict.get('note'):
                            del movie['note']
        self.save_data(users_list)

    @staticmethod
    def get_new_id(data):
        """Returns new id based on data"""
        if len(data) < 1:
            return 1
        return max(item["id"] for item in data) + 1

    def get_new_id_for(self, user_id=None):
        """If user_id is None returns new id based on users,
        otherwise, returns new id based on movies for specific user"""
        if user_id is None:
            return self.get_new_id(self.get_all_users())
        else:
            return self.get_new_id(self.get_user_movies(user_id))
