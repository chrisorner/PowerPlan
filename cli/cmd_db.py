import click

from flask import current_app
from flask.cli import with_appcontext

from sqlalchemy_utils import database_exists, create_database

from energyapp.extensions import db as db_ext


@click.group()
def db():
    """ Run PostgreSQL related tasks. """
    pass


@db.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
@with_appcontext
def init(with_testdb):
    """
    Initialize the database.

    :param with_testdb: Create a test database
    :return: None
    """
    db_ext.drop_all()
    db_ext.create_all()

    if with_testdb:
        db_uri = '{0}_test'.format(
                current_app.config['SQLALCHEMY_DATABASE_URI'])

        if not database_exists(db_uri):
            create_database(db_uri)

    return None


@db.command()
@with_appcontext
def seed():
    """
    Seed the database with an initial user.

    :return: User instance
    """
    app_config = current_app.config

    if User.find_by_identity(app_config['SEED_ADMIN_EMAIL']) is not None:
        return None

    params = {
        'role': 'admin',
        'email': app_config['SEED_ADMIN_EMAIL'],
        'password': app_config['SEED_ADMIN_PASSWORD']
    }

    return User(**params).save()


@db.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
@click.pass_context
@with_appcontext
def reset(ctx, with_testdb):
    """
    Init and seed automatically.

    :param with_testdb: Create a test database
    :return: None
    """
    ctx.invoke(init, with_testdb=with_testdb)
    ctx.invoke(seed)

    return None
