# Dash app initialization
import os

import dash
import dash_bootstrap_components as dbc
from flask_login import LoginManager, UserMixin

# local imports
from utilities.auth import db, User as Base
from utilities.config import config, engine

# dash application
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.COSMO,
    ],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
            "description": "Influential Users Web Platform",
            "author": "Alexandru Grigoras"
        }
    ],
)

server = app.server
app.config.suppress_callback_exceptions = True
app.title = 'Influential Users'

# config
server.config.update(
    SECRET_KEY=os.urandom(20),
    SQLALCHEMY_DATABASE_URI=config.get('database', 'con'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(server)

# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


# Create User class with UserMixin
class User(UserMixin, Base):
    pass


# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
