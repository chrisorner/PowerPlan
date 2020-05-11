import dash
from flask import Flask
from flask.helpers import get_root_path
from energyapp.extensions import debug_toolbar, db
from energyapp.blueprints.page import page
import os


def create_app():
    """
    Create a Flask application using the app factory pattern.

    :return: Flask app
    """
    server = Flask(__name__, instance_relative_config=True)

    server.config.from_object('config.settings')
    server.config.from_pyfile('settings.py', silent=True)

    from energyapp.dashapp1.layout import layout as layout1
    from energyapp.dashapp1.callbacks import register_callbacks as register_callbacks1
    register_dashapp(server, 'Dashapp 1', 'dashboard', layout1, register_callbacks1)

    server.register_blueprint(page)
    extensions(server)


    return server



def register_dashapp(app, title, base_pathname, layout, register_callbacks_fun):
    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
    external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css']

    my_dashapp = dash.Dash(__name__,
                           server=app,
                           url_base_pathname=f'/{base_pathname}/',
                           assets_folder=get_root_path(__name__) + f'/{base_pathname}/assets/',
                           serve_locally = False,
                           external_stylesheets=external_stylesheets,
                           meta_tags=[meta_viewport])


    with app.app_context():
        my_dashapp.title = title
        my_dashapp.layout = layout
        register_callbacks_fun(my_dashapp)


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    #debug_toolbar.init_app(app)
    db.init_app(app)

    return None