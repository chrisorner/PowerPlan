import dash
import os
from flask import Flask
from flask.helpers import get_root_path
from flask_login import login_required
from celery import Celery
from itsdangerous import URLSafeTimedSerializer
from werkzeug.debug import DebuggedApplication


from energyapp.extensions import debug_toolbar, db, mail,login_manager
from energyapp.blueprints.admin import admin
from energyapp.blueprints.page import page
from energyapp.blueprints.contact import contact
from energyapp.blueprints.user import user
from energyapp.blueprints.user.models import User
from cli import register_cli_commands
from energyapp.api.resources import SolarPower, Consumption
from flask_restful import Api
from flask_cors import CORS
from config.settings import Config


# define celery tasks
CELERY_TASK_LIST = [
    'energyapp.blueprints.contact.tasks'
]


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    # Required to access database in a task. Copied from flask docs
    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    """
    Create a Flask application using the app factory pattern.

    :return: Flask app
    """
    server = Flask(__name__)
    server.config.from_object(Config)
    api = Api(server)
    CORS(server)


#    if settings_override:
 #       server.config.update(settings_override)

    #server.logger.setLevel(server.config['LOG_LEVEL'])

    from energyapp.dashapp1.layout import layout as layout1
    from energyapp.dashapp1.callbacks import register_callbacks as register_callbacks1
    register_dashapp(server, 'Dashapp 1', 'profile', layout1, register_callbacks1)

    from energyapp.dashapp2.layout import layout as layout2
    from energyapp.dashapp2.callbacks import register_callbacks as register_callbacks2
    register_dashapp(server, 'Dashapp 2', 'simulation', layout2, register_callbacks2)

    server.register_blueprint(page)
    server.register_blueprint(contact)
    server.register_blueprint(user)
    server.register_blueprint(admin)
    register_cli_commands(server)
    authentication(server, User)
    extensions(server)

    if server.debug:
        server.wsgi_app = DebuggedApplication(server.wsgi_app, evalex=True)

    # api endpoints
    api.add_resource(SolarPower, '/solar')
    api.add_resource(Consumption, '/consumption')

    return server


def register_dashapp(app, title, base_pathname, layout, register_callbacks_fun):
    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
    external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css']

    my_dashapp = dash.Dash(__name__,
                           server=app,
                           url_base_pathname=f'/{base_pathname}/',
                           external_stylesheets=external_stylesheets,
                           meta_tags=[meta_viewport])

    with app.app_context():
        my_dashapp.title = title
        my_dashapp.layout = layout
        register_callbacks_fun(my_dashapp)
    _protect_dashviews(my_dashapp)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(dashapp.server.view_functions[view_func])


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    #debug_toolbar.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    return None


def authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)