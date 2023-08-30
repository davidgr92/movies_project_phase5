import os

DATA_FILES_PATH = "data_manager\\data"
SQLITE_FILE_NAME = "data.sqlite"
SECRET_KEY = "super secret key"


def get_project_dir_abs_path():
    return os.path.abspath(os.path.dirname(__file__))


def get_folder_path_in_root_by_name(folder_name):
    return os.path.join(get_project_dir_abs_path(),
                        folder_name)


def get_sqlite_path():
    return os.path.join(get_project_dir_abs_path(),
                        DATA_FILES_PATH,
                        SQLITE_FILE_NAME)


def get_sqlite_db_uri():
    return "sqlite:///" + get_sqlite_path()
