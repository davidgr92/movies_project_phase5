from flask import Flask, render_template, request, redirect, url_for, abort, Blueprint
from data_manager.dm_json import JSONDataManager
from apis.omdb_api import MovieAPIConnection
from auth_routes import auth as auth_blueprint, login_manager, bcrypt


# Flask app and data manager configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
data_manager = JSONDataManager()
login_manager.init_app(app)
bcrypt.init_app(app)

# ================================ Auth, Login & Profile ============

# blueprint for auth routes in our app
app.register_blueprint(auth_blueprint)

# =========================== End new edits ======================


@app.route('/')
def index():
    return render_template('index.html', title='Created by David G.')


@app.route('/users')
def list_users():
    """Returns main page - lists all users"""
    users = data_manager.get_all_users()
    return render_template('users.html', title='Users',
                           users=users)


@app.route('/users/<int:user_id>')
def get_user_movies(user_id):
    """Returns specific user movies list, handles wrong id error"""
    user = data_manager.get_user_by_key(user_id)
    if not data_manager.is_user_key_exists(user_id):
        abort(404, "Failed to find user with this ID.")
    return render_template('user_movies.html',
                           title=f"{user['name']}'s Movies",
                           user=user)


@app.route('/users/<int:user_id>/delete/', methods=['DELETE'])
def delete_user(user_id):
    """Deletes user from data file, handles wrong id error"""
    data_manager.delete_user(user_id)
    if not data_manager.is_user_key_exists(user_id):
        abort(404, "Failed to find user with this ID.")
    return ''


@app.route('/add_user', methods=['GET', 'POST'])
def add_new_user():
    """When used with GET method, returns form page to register a new user,
    When used with POST method, validates data and sign up the user.
    Shows errors and success message accordingly."""
    if request.method == 'POST':
        users = data_manager.get_all_users()
        new_user = {"id": data_manager.get_new_id(users),
                    "name": request.form.get('name'),
                    "movies": []}
        if new_user['name'] == '':
            error = "Invalid new user request - provided empty name"
            return render_template('add_user.html', title='Add New User',
                                   heading='Add new user',
                                   error_message=error)
        data_manager.add_user(new_user)
        success = "User was successfully created! Now you can add a movie."
        return render_template('add_user_movie.html',
                               title='Add New Favorite Movie',
                               user_id=new_user['id'],
                               success_message=success)
    return render_template('add_user.html', title='Add New User',
                           heading='Add new user')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_new_user_movie(user_id):
    """When used with GET method, returns form page to add new movie,
    When used with POST method sends request to omdb movies api to get
    movie details, and adds to data file. Handles errors with user id,
    movie api and data manager"""
    if request.method == 'GET':
        if not data_manager.is_user_key_exists(user_id):
            abort(404, "Failed to find user with this ID.")
        return render_template('add_user_movie.html',
                               title='Add New Favorite Movie',
                               user_id=user_id)

    # In case of a POST request method
    movies = data_manager.get_user_movies(user_id)
    connection = MovieAPIConnection()
    new_movie = connection.get_movie_data(request.form.get('movie-name'))

    # Handle errors in the response from the MovieAPI
    if 'error' in new_movie:
        error = new_movie['error']
        return render_template('add_user_movie.html',
                               title='Add New Favorite Movie',
                               user_id=user_id,
                               error_message=error)

    new_movie_id = data_manager.get_new_id(movies)
    new_movie.update({'id': new_movie_id})

    # Handle errors from the data manager
    try:
        data_manager.add_user_movie(user_id, new_movie)
    except ValueError as error:
        return render_template('add_user_movie.html',
                               title='Add New Favorite Movie',
                               user_id=user_id,
                               error_message=error)

    return redirect(url_for('get_user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>',
           methods=['GET', 'POST'])
def update_user_movie(user_id, movie_id):
    """When used with GET method, returns form page to update the movie,
    When used with POST method updates the movie details on file.
    Handles wrong id error"""
    if request.method == 'GET':
        if not data_manager.is_user_key_exists(user_id):
            abort(404, "Failed to find user with this ID.")
        if not data_manager.is_movie_id_exists(user_id, movie_id):
            abort(404, "Failed to find movie with this ID.")
        movie = data_manager.get_user_single_movie(user_id, movie_id)
        return render_template('update_user_movie.html', user_id=user_id,
                               title=f'Updating Movie: {movie["name"]}',
                               movie=movie)

    # In case of a POST request method
    updated_movie = dict(request.form)
    data_manager.update_user_movie(user_id, movie_id, updated_movie)
    return redirect(url_for('get_user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>',
           methods=['DELETE'])
def delete_user_movie(user_id, movie_id):
    """Deletes a movie from user's movie list in data file"""
    data_manager.delete_user_movie(user_id, movie_id)
    return ''


@app.errorhandler(404)
def error_404(error):
    """Renders 404.html page when user reaches a Page Not Found error page"""
    return render_template('errors/404.html', title="Page not found 404",
                           error_message=error)


@app.errorhandler(400)
def error_400(error):
    """Renders 400.html page when user reaches a Bad Request error page"""
    return render_template('errors/400.html', title="Bad request 400",
                           error_message=error)


if __name__ == '__main__':
    app.run(debug=True)
