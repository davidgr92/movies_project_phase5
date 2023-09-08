from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import get_sqlite_db_uri, SECRET_KEY,\
    get_folder_path_in_root_by_name


app = Flask(__name__,
            static_folder=get_folder_path_in_root_by_name("static"),
            template_folder=get_folder_path_in_root_by_name("templates"))

app.config['SQLALCHEMY_DATABASE_URI'] = get_sqlite_db_uri()
app.secret_key = SECRET_KEY

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "danger"


# Registering blueprints
from my_app.auth.routes import auth_bp
from my_app.main.routes import main_bp
from my_app.user.routes import user_bp
from my_app.api.routes import api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(user_bp)
app.register_blueprint(api_bp)
