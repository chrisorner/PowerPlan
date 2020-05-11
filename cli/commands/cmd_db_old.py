import click
from energyapp import create_app
from energyapp import db
from flask.cli import with_appcontext


@click.group()
def cli():
    """ Run Database  related tasks. """
    pass


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    click.echo('Here it works')
    #db.init_db()
    #click.echo('Initialized the database.')


cli.add_command(init_db_command)